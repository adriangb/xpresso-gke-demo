import * as tls from "@pulumi/tls";
import * as k8s from "@pulumi/kubernetes";
import * as random from "@pulumi/random";
import * as pulumi from "@pulumi/pulumi";
import * as cloudsql from "./cloudsql";
import * as cluster from "./cluster";
import * as iam from "./iam";


const key = new tls.PrivateKey("edgeDB", {
  algorithm: "RSA",
  rsaBits: 2048,
});

const cert = new tls.SelfSignedCert("edgedb", {
  keyAlgorithm: "RSA",
  privateKeyPem: key.privateKeyPem,
  allowedUses: [],
  validityPeriodHours: 24 * 365,
  subjects: [],
});

const credentialsSecret = new k8s.core.v1.Secret(
  "edgedb-tls-credentials",
  {
    stringData: {
      "tls.cert": cert.certPem,
      "tls.key": key.privateKeyPem,
    },
    type: "kubernetes.io/tls",
  },
  { provider: cluster.provider }
);

export const edgedbCertificate = new k8s.core.v1.Secret(
    "edgedb-tls-certificate",
    {
      stringData: {
        "tls.cert": cert.certPem,
      },
      type: "Opaque",
    },
    { provider: cluster.provider }
);

const edgedbServiceAccount = new k8s.core.v1.ServiceAccount(
  "app",
  {
    metadata: {
      name: "edgedb-service-account",
      annotations: {
        // This lets this k8s SA act as the GCP SA via Workload Identity
        "iam.gke.io/gcp-service-account": iam.serviceAccount.email,
      },
    },
  },
  { provider: cluster.provider }
);
const edgedbRole = new k8s.rbac.v1.Role("edgedb-cert-reader", {
  metadata: {
    name: "edgedb-key-reader",
  },
  rules: [{ resourceNames: [credentialsSecret.metadata.name], verbs: ["get"] }],
});
const edgedbRoleBinding = new k8s.rbac.v1.RoleBinding("read-edgedb-key", {
  metadata: { name: "read-edgedb-key" },
  roleRef: {
    name: edgedbRole.metadata.name,
    kind: "Role",
    apiGroup: "rbac.authorization.k8s.io",
  },
  subjects: [
    {
      kind: "ServiceAccount",
      name: edgedbServiceAccount.metadata.name,
    },
  ],
});

export const connection = {
    port: 5655,
    database: "edgedb",
    user: "edgedb",
    password: new random.RandomPassword("edgedb-cloudsql-password", {
        length: 8,
        special: false,
    }).result,
};

const createDatabase = pulumi.interpolate`create database ${connection.database};`;
const createUser = pulumi.interpolate`create superuser role ${connection.user} { set password := '${connection.password}'; };`;
const bootstrap = pulumi.interpolate`${createDatabase}${createUser}`

const edgedbDeployment = new k8s.apps.v1.Deployment(
  "edgedb-deployment",
  {
    spec: {
      selector: { matchLabels: { app: "edgedb" } },
      replicas: 1,
      template: {
        metadata: {
          labels: { app: "edgedb" },
        },
        spec: {
          containers: [
            {
              name: "cloudsql-proxy",
              image: "gcr.io/cloudsql-docker/gce-proxy:1.28.1",
              command: [
                "/cloud_sql_proxy",
                pulumi.interpolate`-instances=${cloudsql.dbConnectionString}=tcp:5432`,
                "-enable_iam_login",
                "-structured_logs",
                "-use_http_health_check",
              ],
              livenessProbe: {
                  httpGet: {
                      path: "/liveness",
                      port: 8090,
                  }
              },
              readinessProbe: {
                  httpGet: {
                      path: "/readiness",
                      port: 8090,
                  }
              }
            },
            {
              name: "edgedb",
              image: "edgedb/edgedb",
              env: [
                {
                  name: "EDGEDB_SERVER_TLS_CERT",
                  valueFrom: {
                    secretKeyRef: {
                      name: credentialsSecret.metadata.name,
                      key: "tls.cert",
                    },
                  },
                },
                {
                  name: "EDGEDB_SERVER_TLS_KEY",
                  valueFrom: {
                    secretKeyRef: {
                      name: credentialsSecret.metadata.name,
                      key: "tls.key",
                    },
                  },
                },
                { name: "EDGEDB_SERVER_TLS_CERT_MODE", value: "require_file" },
                {
                  name: "EDGEDB_SERVER_BACKEND_DSN",
                  value: pulumi.interpolate`postgres://${cloudsql.user.name}@localhost:5432`,
                },
                { name: "EDGEDB_SERVER_PORT", value: connection.port.toString() },
                { 
                    name: "EDGEDB_SERVER_DATABASE",
                    value: pulumi.interpolate`create database ${connection.database};create role ${connection.user} { set password := '${connection.password}'; }`,
                },
              ],
              ports: [{ containerPort: connection.port }],
              livenessProbe: {
                initialDelaySeconds: 15,
                httpGet: {
                  path: "/server/status/ready",
                  port: connection.port,
                },
              },
            },
          ],
          serviceAccountName: edgedbServiceAccount.metadata.name,
        },
      },
    },
  },
  {
    provider: cluster.provider, dependsOn: [edgedbRoleBinding],
  }
);

export const edgedbService = new k8s.core.v1.Service(
  "edgedb",
  {
    metadata: { labels: edgedbDeployment.metadata.labels },
    spec: {
      type: "ClusterIP",
      ports: [{ port: connection.port, targetPort: connection.port }],
      selector: edgedbDeployment.spec.template.metadata.labels,
    },
  },
  { provider: cluster.provider }
);

import { readFileSync } from "fs";
import * as docker from "@pulumi/docker";
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as cluster from "./cluster";
import * as config from "./config";
import * as db from "./cloudsql";
import * as iam from "./iam";
import { dockerRegistry, dockerRegistryId } from "./artifact-registry";
import * as edgedb from "./edgedb";

const apiImage = new docker.Image(
  "app",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/api:latest`,
    build: {
      context: "../app",
      target: "api",
    },
  },
  { dependsOn: [dockerRegistry] }
);

// Create a k8s service account for the app
const appServiceAccount = new k8s.core.v1.ServiceAccount(
  "app",
  {
    metadata: {
      name: "app-service-account",
    },
  },
  { provider: cluster.provider }
);
const edgedbClientRole = new k8s.rbac.v1.Role("edgedb-cert-reader", {
  metadata: {
    name: "edgedb-cert-reader",
  },
  rules: [{ resourceNames: [edgedb.edgedbCertificate.metadata.name], verbs: ["get"] }],
});
const edgedbClientRoleBinding = new k8s.rbac.v1.RoleBinding("read-edgedb-cert", {
  metadata: { name: "read-edgedb-cert" },
  roleRef: {
    name: edgedbClientRole.metadata.name,
    kind: "Role",
    apiGroup: "rbac.authorization.k8s.io",
  },
  subjects: [
    {
      kind: "ServiceAccount",
      name: edgedb.edgedbCertificate.metadata.name,
    },
  ],
});
// Create the deployment and service for our app
const appLabels = { app: "app" };
const appDeployment = new k8s.apps.v1.Deployment(
  "app-deployment",
  {
    spec: {
      selector: { matchLabels: appLabels },
      replicas: 2,
      template: {
        metadata: {
          labels: appLabels,
        },
        spec: {
          containers: [
            {
              name: "app",
              image: apiImage.imageName,
              env: [
                { name: "LOG_LEVEL", value: "INFO" },
                { name: "APP_PORT", value: config.appPort.toString() },
                { name: "APP_HOST", value: "0.0.0.0" },
                { name: "SERVICE_NAME", value: "api" },
                { name: "VERSION", value: projectVersion },
                { name: "ENV", value: pulumi.getStack() },
                { name: "DB_HOST", value: "localhost" },
                { name: "DB_PORT", value: "5432" },
                { name: "DB_USERNAME", value: db.user.name },
                { name: "DB_DATABASE_NAME", value: edgedb.database },
                {
                  name: "EDGEDB_SERVER_TLS_CERT",
                  valueFrom: {
                    secretKeyRef: {
                      name: edgedb.edgedbCertificate.metadata.name,
                      key: "tls.cert",
                    },
                  },
                },
              ],
              ports: [{ containerPort: config.appPort }],
              livenessProbe: {
                initialDelaySeconds: 15,
                periodSeconds: 10,
                httpGet: {
                  path: "/health",
                  port: config.appPort,
                },
              },
            },
          ],
          serviceAccount: appServiceAccount.metadata.name,
        },
      },
    },
  },
  {
    provider: cluster.provider,
  }
);
export const appService = new k8s.core.v1.Service(
  "app-service",
  {
    metadata: { labels: appDeployment.metadata.labels },
    spec: {
      type: "LoadBalancer",
      ports: [{ port: 80, targetPort: config.appPort }],
      selector: appDeployment.spec.template.metadata.labels,
    },
  },
  { provider: cluster.provider, dependsOn: [appDeployment] }
);

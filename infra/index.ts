// Copyright 2016-2021, Pulumi Corporation.  All rights reserved.

import { readFileSync } from "fs";
import * as docker from "@pulumi/docker";
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as cluster from "./cluster";
import * as config from "./config";
import * as db from "./db";
import * as iam from "./iam";
import { dockerRegistry, dockerRegistryId } from "./artifact-registry";
import { execSync } from "child_process";

// Tag images as name:${projectVersion}-${gitHash}
// This makes them human-readable and also deterministically linkable to code
const gitHash = execSync("git rev-parse --short HEAD").toString().trim();
const projectVersion = readFileSync("../VERSION.txt", "utf8").trim();

// We build and push the image to the GCP project's Artifact Registry.
// Make sure docker is configured to use docker registry by running
// > gcloud auth configure-docker
// before running pulumi up
const migrationsImage = new docker.Image(
  "migrations",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/migrations:${projectVersion}-${gitHash}`,
    build: {
      context: "../app",
      target: "migrations",
    },
  },
  { dependsOn: [dockerRegistry] }
);
const apiImage = new docker.Image(
  "app",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/api:${projectVersion}-${gitHash}`,
    build: {
      context: "../app",
      target: "api",
    },
  },
  { dependsOn: [dockerRegistry] }
);

// Create a k8s service account that binds our GCP service account
const kubernetesServiceAccount = new k8s.core.v1.ServiceAccount(
  "app",
  {
    metadata: {
      name: config.k8sServiceAccountName,
      annotations: {
        "iam.gke.io/gcp-service-account": iam.serviceAccount.email,
      },
    },
  },
  { provider: cluster.provider, dependsOn: [cluster.provider] }
);
// Create a secret with our token signing key
const tokenSigningKey = new k8s.core.v1.Secret(
  "token-signing-key",
  {
    stringData: {
      key: new random.RandomPassword("tokenSigningKey", {
        length: 16,
        special: false,
      }).result,
    },
  },
  { provider: cluster.provider }
);
// Create a Kubernetes job to run database migrations
const migrationsJob = new k8s.batch.v1.Job(
  "migrations",
  {
    spec: {
      template: {
        spec: {
          containers: [
            {
              name: "cloudsql-proxy",
              // Note that we use the buster image because it has
              // GNU coreutils, which we need for the --preserve-status
              // option on timeout
              image: "gcr.io/cloudsql-docker/gce-proxy:1.28.1-buster",
              // Running a sidecar in a job is problematic because the sidecar
              // will never exit and thus the job will never "complete"
              // There are many workarounds to this, the one we use here was chosen
              // because it does not require any modification of the app's migration container
              // (which should not know it's running in k8s) or the CloudSQL Proxy container
              // (which we don't have direct control over).
              // What we do is use timeout to send a SIGTERM to the proxy's process after 30 seconds.
              // With the -term_timeout=600s flag the proxy will then
              // wait _up to_ 600s for all connections to close and then
              // exit gracefully (if all connections closed)
              // So as long as the migrations _start_ within 30s
              // and finish within 600s, then the job will be marked as successful
              // Of course if the migrations fail, it will be marked as failed
              // because one of the pods exited with a non-zero status code
              command: [
                "timeout",
                "--preserve-status",
                "-s",
                "SIGTERM",
                "30s",
                "/cloud_sql_proxy",
                pulumi.interpolate`-instances=${db.dbConnectionString}=tcp:5432`,
                "-enable_iam_login",
                "-structured_logs",
                "-term_timeout=3600s",
              ],
            },
            {
              name: "migrations",
              image: migrationsImage.imageName,
              imagePullPolicy: "IfNotPresent",
              env: [
                { name: "DB_HOST", value: "localhost" },
                { name: "DB_PORT", value: "5432" },
                { name: "DB_USERNAME", value: db.user.name },
                { name: "DB_DATABASE_NAME", value: db.db.name },
                { name: "VERSION", value: projectVersion },
                { name: "ENV", value: pulumi.getStack() },
                { name: "SERVICE_NAME", value: "migrations" },
              ],
            },
          ],
          restartPolicy: "Never",
          serviceAccount: kubernetesServiceAccount.metadata.name,
        },
      },
    },
  },
  {
    provider: cluster.provider,
    dependsOn: [apiImage, kubernetesServiceAccount],
  }
);
// Deploy the app container as a Kubernetes load balanced service.
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
              name: "cloudsql-proxy",
              image: "gcr.io/cloudsql-docker/gce-proxy:1.28.1",
              command: [
                "/cloud_sql_proxy",
                pulumi.interpolate`-instances=${db.dbConnectionString}=tcp:5432`,
                "-enable_iam_login",
                "-structured_logs",
                "-structured_logs",
              ],
            },
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
                { name: "DB_DATABASE_NAME", value: db.db.name },
                {
                  name: "TOKEN_SIGNING_KEY",
                  valueFrom: {
                    secretKeyRef: {
                      name: tokenSigningKey.metadata.name,
                      key: "key",
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
          serviceAccount: kubernetesServiceAccount.metadata.name,
        },
      },
    },
  },
  {
    provider: cluster.provider,
    dependsOn: [apiImage, migrationsJob, kubernetesServiceAccount],
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

import * as docker from "@pulumi/docker";
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as cluster from "./cluster";
import * as config from "./config";
import { dockerRegistryId } from "./artifact-registry";
import { execSync } from "child_process";

const gitHash = execSync("git rev-parse --short HEAD").toString().trim();

// We build and push the image to the GCP project's Artifact Registry.
// Make sure docker is configured to use docker registry by running
// > gcloud auth configure-docker
// before running pulumi up
const gunicornImage = new docker.Image(
  "gunicorn-image",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/gunicorn:${gitHash}`,
    build: {
      context: "../",
      dockerfile: "../Dockerfile",
      target: "gunicorn",
      extraOptions: ["--platform", "amd64"], // for compatibility with running on ARM MacBooks
    },
  }
);
const uvicornImage = new docker.Image(
  "uvicorn-image",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/uvicorn:${gitHash}`,
    build: {
      context: "../",
      dockerfile: "../Dockerfile",
      target: "uvicorn",
      extraOptions: ["--platform", "amd64"], // for compatibility with running on ARM MacBooks
    },
  }
);
const benchImage = new docker.Image(
  "bench-image",
  {
    imageName: pulumi.interpolate`us-docker.pkg.dev/${config.projectId}/${dockerRegistryId}/bench:${gitHash}`,
    build: {
      context: "../",
      dockerfile: "../Dockerfile",
      target: "bench",
      extraOptions: ["--platform", "amd64"], // for compatibility with running on ARM MacBooks
    },
  }
);

const uvicornDeployment = new k8s.apps.v1.Deployment(
  "uvicorn-deployment",
  {
    metadata: {
      name: "uvicorn",
    },
    spec: {
      replicas: 4 * 8,
      selector: { matchLabels: {app: "uvicorn"} },
      template: {
        metadata: {
          labels: {app: "uvicorn"},
        },
        spec: {
          containers: [
            {
              name: "uvicorn",
              image: uvicornImage.imageName,
              ports: [{ containerPort: 80 }],
              resources: {
                requests: {
                  cpu: "1000m",
                  memory: "512m",
                },
              },
            },
          ],
        },
      },
    },
  },
  {
    provider: cluster.provider,
  }
);
const uvicornService = new k8s.core.v1.Service(
  "uvicorn-service",
  {
    metadata: { labels: uvicornDeployment.metadata.labels },
    spec: {
      type: "LoadBalancer",
      ports: [{ port: 80 }],
      selector: uvicornDeployment.spec.template.metadata.labels,
    },
  },
  { provider: cluster.provider}
);
export const uvicornAppAddress = uvicornService.status.apply(s => `http://${s.loadBalancer.ingress[0].ip}:80`);

const gunicornDeployment = new k8s.apps.v1.Deployment(
  "gunicorn-deployment",
  {
    metadata: {
      name: "gunicorn",
    },
    spec: {
      replicas: 4,
      selector: { matchLabels: {app: "gunicorn"} },
      template: {
        metadata: {
          labels: {app: "gunicorn"},
        },
        spec: {
          containers: [
            {
              name: "gunicorn",
              image: gunicornImage.imageName,
              ports: [{ containerPort: 80 }],
              resources: {
                requests: {
                  cpu: "8000m",
                  memory: "4096m",
                },
              },
            },
          ],
        },
      },
    },
  },
  {
    provider: cluster.provider,
  }
);
const gunicornService = new k8s.core.v1.Service(
  "gunicorn-service",
  {
    metadata: { labels: gunicornDeployment.metadata.labels },
    spec: {
      type: "LoadBalancer",
      ports: [{ port: 80 }],
      selector: gunicornDeployment.spec.template.metadata.labels,
    },
  },
  { provider: cluster.provider}
);
export const gunicornAppAddress = gunicornService.status.apply(s => `http://${s.loadBalancer.ingress[0].ip}:80`);

const benchmarkDeployment = new k8s.apps.v1.Deployment(
  "bench-deployment",
  {
    metadata: {
      name: "bench",
    },
    spec: {
      replicas: 1,
      selector: { matchLabels: {app: "bench"} },
      template: {
        metadata: {
          labels: {app: "bench"},
        },
        spec: {
          containers: [
            {
              name: "bench",
              image: benchImage.imageName,
              ports: [{ containerPort: 80 }],
              resources: {
                // Give this thing hella resources to make
                // sure it's not the bottleneck / equalizer
                requests: {
                  cpu: "1600m",
                  memory: "16Gi",
                },
              },
              env: [
                {
                  name: "GUNICORN_HOST",
                  value: gunicornAppAddress,
                },
                {
                  name: "UVICORN_HOST",
                  value: uvicornAppAddress,
                }
              ]
            },
          ],
        },
      },
    },
  },
  {
    provider: cluster.provider,
  }
);
const benchmarkService = new k8s.core.v1.Service(
  "bench-service",
  {
    metadata: { labels: benchmarkDeployment.metadata.labels },
    spec: {
      type: "LoadBalancer",
      ports: [{ port: 80 }],
      selector: benchmarkDeployment.spec.template.metadata.labels,
    },
  },
  { provider: cluster.provider}
);
export const benchAppAddress = benchmarkService.status.apply(s => `http://${s.loadBalancer.ingress[0].ip}:80`);

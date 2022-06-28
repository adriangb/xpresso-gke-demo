import * as gcloud from "@pulumi/google-native";
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as config from "./config";

const cluster = new gcloud.container.v1.Cluster("cluster", {
  location: "us-central1",
  autopilot: { enabled: true },
  project: config.projectId,
  releaseChannel: {
    channel: gcloud.container.v1.ReleaseChannelChannel.Regular,
  },
  workloadIdentityConfig: {
    workloadPool: `${config.projectId}.svc.id.goog`,
  },
});

// Manufacture a GKE-style Kubeconfig. Note that this is slightly "different" because of the way GKE requires
// gcloud to be in the picture for cluster authentication (rather than using the client cert/key directly).
export const kubeConfig = pulumi
  .all([cluster.name, cluster.endpoint, cluster.location, cluster.masterAuth])
  .apply(([name, endpoint, location, auth]) => {
    const context = `${config.projectId}_${location}_${name}`;
    return `apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: ${auth.clusterCaCertificate}
    server: https://${endpoint}
  name: ${context}
contexts:
- context:
    cluster: ${context}
    user: ${context}
  name: ${context}
current-context: ${context}
kind: Config
preferences: {}
users:
- name: ${context}
  user:
    auth-provider:
      config:
        cmd-args: config config-helper --format=json
        cmd-path: gcloud
        expiry-key: '{.credential.token_expiry}'
        token-key: '{.credential.access_token}'
      name: gcp
`;
  });

// Export a Kubernetes provider instance that uses our cluster from above.
export const provider = new k8s.Provider(
  "gke-k8s",
  {
    kubeconfig: kubeConfig,
  },
  {
    dependsOn: [cluster],
  }
);

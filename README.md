# Containerized Python Xpresso app, deployed to GKE via Pulumi

This example is a full end to end example of delivering a containerized Xpresso app.

Using an infrastructure as code approach, running this repo will:

- Provision a GKE cluster
- Provisions a fully managed Google Cloud SQL PostgreSQL database
- Builds a containerized Xpresso app, and it to the Google Artifact Registry
- Deploys that container image as a Kubernetes Service inside of the provisioned GKE cluster

## Prerequisites

Before trying to deploy this example, please make sure you have performed all of the following tasks:

- [downloaded and installed the Pulumi CLI](https://www.pulumi.com/docs/get-started/install/).
- [downloaded and installed Docker](https://docs.docker.com/install/)
- [signed up for Google Cloud](https://cloud.google.com/free/)
- [followed the instructions here](https://www.pulumi.com/docs/intro/cloud-providers/gcp/setup/) to connect Pulumi to your Google Cloud account.

This example assumes that you have Google Cloud's `gcloud` CLI on your path.
This is installed as part of the
[Google Cloud SDK](https://cloud.google.com/sdk/).

As part of this example, we will setup and deploy a Kubernetes cluster on GKE.
You may also want to install [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) if you would like to directly interact with the underlying Kubernetes cluster.

## Running the Example

### Set up your GCP Project

You'll need to create a new GCP project (or use an existing one).
Enable the following APIs in GCP if they are not already enabled:

- [Artifact Registry](https://cloud.google.com/artifact-registry/docs/enable-service#enable)
- [Kubernetes Engine](https://cloud.google.com/kubernetes-engine/docs/quickstart#before-you-begin)
- [Cloud SQL](https://cloud.google.com/sql/docs/mysql/admin-api#enable_the_api)

If you've configured `gcloud` locally and pointed it at your project you can run:

```shell
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable container.googleapis.com
```

We'll be pushing a docker image to Artifact Registry, so configure docker for authentication:

```shell
gcloud auth configure-docker
```

Now you're ready to get started with the repo.
Clone the repo then cd into the infra directory:

```shell
cd infra
```

Now set up the Pulumi stack:

```shell
pulumi stack init dev
```

Set the required configuration variables for this program:

```shell
pulumi config set xpresso-gke-demo:project [your-gcp-project-here]
pulumi config set xpresso-gke-demo:region us-west1 # any valid region
```

Since we will use Google's Artifact Registry for hosting the Docker image, we need to configure your machine's Docker to be able to authenticate with GCR:

```shell
gcloud auth configure-docker
```

Deploy everything with the `pulumi up` command.
This provisions all the GCP resources necessary, including your GKE cluster and database, as well as building and publishing your container image, all in a single gesture:

```shell
pulumi up
```

This will show you a preview, ask for confirmation, and then chug away at provisioning your cluster.

```shell
pulumi destroy
pulumi stack rm
```

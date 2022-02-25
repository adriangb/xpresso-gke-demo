# Containerized Python app, deployed to GKE via Pulumi

This example is a full end to end example of delivering a containerized Xpresso app.

Using an infrastructure as code approach, running this repo will:

- Provision a GKE cluster
- Provisions a fully managed Google Cloud SQL PostgreSQL database
- Builds a containerized Python app, and pushes it to Google Artifact Registry
- Deploys that container image as a Kubernetes Service in the GKE cluster

## Infrastructure

See [/infrastrcture](infrastructrue/README.md) for instructions on getting the infrastructure up.

## App

See [/app](app/README.md) for instructions on getting the app set up.

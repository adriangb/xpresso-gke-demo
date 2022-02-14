import * as classic from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as gcloud from "@pulumi/google-native";
import { dbName, project } from "./config";
import * as iam from "./iam"

// Provision a database for our app.
export const instance = new gcloud.sqladmin.v1.Instance("web-db", {
    databaseVersion: "POSTGRES_14",
    project: project,
    settings: {
        settingsVersion: "1",
        tier: "db-f1-micro",
        databaseFlags: [
            { name: "cloudsql.iam_authentication", value: "on"}
        ],
        availabilityType: "REGIONAL",
        backupConfiguration: {
            enabled: true,
        },
    },
});

export const db = new gcloud.sqladmin.v1.Database("db", {
    name: dbName,
    instance: instance.name,
    project: project,
});

// Create a user with the configured credentials for the app to use.
// TODO: Switch to google native version when User is supported:
// https://github.com/pulumi/pulumi-google-native/issues/47
export const user = new classic.sql.User("web-db-user", {
    instance: instance.name,
    // The name MUST be the service account email
    // WITHOUT the .gserviceaccount.com suffix
    // See https://cloud.google.com/sql/docs/postgres/iam-logins
    name: iam.serviceAccount.email.apply(v => v.replace(".gserviceaccount.com", "")),
    password: genRandomPassword("dbPassword", 16),
    project: project,
    // Careful here: CLOUD_IAM_SERVICE_ACCOUNT != CLOUD_IAM_USER
    // The latter is for end-user IAM access, not service accounts
    type: "CLOUD_IAM_SERVICE_ACCOUNT",
});

function genRandomPassword(name: string, length: number): pulumi.Output<string> {
    let password = new random.RandomString(name, {
        upper: false,
        number: true,
        special: true,
        length: length,
    }).result;
    return pulumi.secret(password);
};
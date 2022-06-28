import { Config } from "@pulumi/pulumi";

const config = new Config();

export const projectId = config.require("projectId");

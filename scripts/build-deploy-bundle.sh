#!/usr/bin/env bash
# Builds deploy-bundle.zip = taskdef.json + appspec.yaml, the release hand-off to CodeDeploy.
#
# The task definition is NOT kept in this repository. The infrastructure repo
# owns it (CPU, memory, roles, logging). Here we read the current revision from
# ECS and swap the image for the <IMAGE1_NAME> placeholder, which CodePipeline
# replaces with the exact image digest that triggered the release.
set -euo pipefail
: "${TASK_FAMILY:?}" "${CONTAINER_NAME:?}"
OUT_DIR=${1:-build}
mkdir -p "$OUT_DIR"

if ! aws ecs describe-task-definition --task-definition "$TASK_FAMILY" --query taskDefinition --output json > "$OUT_DIR/current.json" 2>/dev/null; then
  echo "::warning::Task definition $TASK_FAMILY not found (first-time bootstrap). Skipping deployment bundle."
  exit 3
fi

jq --arg name "$CONTAINER_NAME" '
  .containerDefinitions |= map(if .name == $name then .image = "<IMAGE1_NAME>" else . end)
  | del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities,
        .registeredAt, .registeredBy, .deregisteredAt)
' "$OUT_DIR/current.json" > "$OUT_DIR/taskdef.json"

grep -q '<IMAGE1_NAME>' "$OUT_DIR/taskdef.json" || { echo "Container $CONTAINER_NAME not in task definition"; exit 1; }
cp deploy/appspec.yaml "$OUT_DIR/appspec.yaml"
(cd "$OUT_DIR" && rm -f deploy-bundle.zip && zip -q deploy-bundle.zip taskdef.json appspec.yaml)
echo "Built $OUT_DIR/deploy-bundle.zip"

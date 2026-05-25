# Hospital Agentic RAG CodePipeline

This package creates an AWS CI/CD pipeline for an OpenAI-backed agentic RAG endpoint. The RAG knowledge source is a text manual at `src/hospital_operations_manual.txt`.

Agents:

- Agent 1: `hospital` handles hospital operations, routing, bed placement, staffing, and escalation coordination.
- Agent 2: `doctor` handles clinical risk review and escalation considerations.
- Agent 3: `nurse` handles bedside handoff, monitoring, and documentation priorities.

## Flow

```text
GitHub
  -> AWS CodePipeline
  -> AWS CodeBuild
  -> pytest and RAG retrieval evaluation
  -> package Lambda artifact
  -> upload artifact to S3
  -> CloudFormation deploys Lambda Function URL
  -> Lambda retrieves manual sections
  -> OpenAI Responses API runs hospital, doctor, and nurse agents
  -> final structured care-coordination response
```

The implementation uses the OpenAI Responses API with structured JSON outputs. OpenAI recommends Responses for new agentic applications, and file/retrieval-style workflows can be grounded through retrieved context or OpenAI file search depending on the architecture. The AWS side uses CodePipeline with a CodeBuild action and CloudFormation deployment.

## Local Test

```bash
cd hospital-agentic-rag-codepipeline
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests
python scripts/evaluate_rag.py
```

Invoke locally without calling OpenAI:

```bash
set APP_MODE=local
python -c "import json; from src.app import lambda_handler; event={'body': open('samples/hospital_event.json').read()}; print(lambda_handler(event, None)['body'])"
```

## OpenAI Secret

Store the API key in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --region us-west-1 \
  --name openai/api-key \
  --secret-string "sk-your-openai-api-key"
```

Pass that secret ARN to the CodePipeline stack as `OpenAIApiKeySecretArn`.

## Deploy CodePipeline

```bash
aws cloudformation deploy \
  --region us-west-1 \
  --template-file hospital-agentic-rag-codepipeline/infrastructure/codepipeline.yaml \
  --stack-name hospital-agentic-rag-cicd \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ProjectName=hospital-agentic-rag \
    ArtifactBucketName=mlopswithsagemaker111 \
    CodeStarConnectionArn=arn:aws:codeconnections:us-west-1:659613508664:connection/4ea8863c-728d-450a-8752-251946939b36 \
    RepositoryId=kalla86840/awsllmagenticrag \
    BranchName=main \
    OpenAIApiKeySecretArn=arn:aws:secretsmanager:us-west-1:659613508664:secret:openai/api-key-6BGXhJ \
    OpenAIModel=gpt-5.2
```

After deployment, read the endpoint URL from the `hospital-agentic-rag-endpoint` CloudFormation stack output named `FunctionUrl`.

## RAG Performance

`scripts/evaluate_rag.py` checks whether the manual retrieves the expected section for chest pain, sepsis, stroke, and nurse handoff prompts. CodeBuild runs this before packaging, so a manual edit that breaks retrieval fails the pipeline before deployment.

## References

- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses/create?api-mode=responses)
- [OpenAI Responses migration guide](https://platform.openai.com/docs/guides/responses-vs-chat-completions)
- [OpenAI file search guide](https://platform.openai.com/docs/guides/tools-file-search/)
- [AWS CodePipeline CodeBuild action reference](https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodeBuild.html)

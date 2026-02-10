import {
    CopilotRuntime,
    copilotRuntimeNextJSAppRouterEndpoint,
    ExperimentalEmptyAdapter
} from "@copilotkit/runtime";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";
import { NextRequest } from "next/server";

// Use EmptyAdapter since LangGraph agent handles the logic
const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
    agents: {
        chestia_recipe_agent: new LangGraphHttpAgent({
            url: process.env.LANGGRAPH_DEPLOYMENT_URL || "http://localhost:8000/copilotkit",
        }) as any,
    },
});

export const POST = async (req: NextRequest) => {
    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
        runtime,
        serviceAdapter,
        endpoint: "/api/copilotkit",
    });

    const response = await handleRequest(req);
    return response;
};
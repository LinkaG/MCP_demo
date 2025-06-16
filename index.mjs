


</HfOption>
<HfOption id="server-implementation" option="javascript">



```javascript
// index.mjs
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
    name: "Weather Service",
    version: "1.0.0"
});

// Tool implementation
server.tool("get_weather",
    { location: z.string() },
    async ({ location }) => ({
        content: [{
            type: "text",
            text: `Weather in ${location}: Sunny, 72°F`
        }]
    })
);

// Resource implementation
server.resource(
    "weather",
    new ResourceTemplate("weather://{location}", { list: undefined }),
    async (uri, { location }) => ({
        contents: [{
            uri: uri.href,
            text: `Weather data for ${location}: Sunny, 72°F`
        }]
    })
);

// Prompt implementation
server.prompt(
    "weather_report",
    { location: z.string() },
    async ({ location }) => ({
        messages: [
            {
                role: "assistant",
                content: {
                    type: "text",
                    text: "You are a weather reporter."
                }
            },
            {
                role: "user",
                content: {
                    type: "text",
                    text: `Weather report for ${location}?`
                }
            }
        ]
    })
);

// Run the server
const transport = new StdioServerTransport();
await server.connect(transport);
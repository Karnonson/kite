1. Since the implementation is split in to two stage (backend and frontend), let’s remove it in kite.
2. In the Founder fast path, the constitution phase is skip
3. The main readme is still written as speckit official readme.
4.Github’s spec kit contributors badges are still on kite

************

1. kite’s cli still uses specify as the logo. It should be KITE
2. The boostrap is failing after the container is build. I just run the curl command in my workspace and got at the end: Error: Must specify either a project name, use '.' for current directory, or use
--here flag
[27823 ms] postCreateCommand from devcontainer.json failed with exit code 1. Skipping any further user-provided commands.
3.When the container is ready, the slash commands are not working automatically. User has to run "kite init .", that’s fine but the docs suppose kite is initialize automatically with copilot as the agent.
4. Kite’s innitialization doesn’t create the .gitignore file.

*************

1. After the disgn phase, add a clarification step to make sure nothing is missing before we start the plan.
2. In the workflow, a agent should gather user preferences regarding frameworks, AI SDK (if applicable), hosting options, ... while making suggestions to guide the user. For AI SDK, especially, the agent should browse the offical docs to see if it can get a MCP connection or a skill on how to use the framework. Example, Mastra has skill and a MCP connection that help ai agent follow mastra’s best practices. Google’s ADK as a mcp server too.
3. After container is built, It should set the branch to main instead of master.
4. The coding agents should avoid outdate framework versions (use the research agent to browse the web for up to date infos). Create the research agent.

************

1. Let’s use tracer bullet style task list in for task generation. Meaning, each phase should be testable by it own. To make sure everything works before moving to the next phase.
2. The frontend and backend tasks should be clearly split so the agents don’t mistakenly complete each other tasks. The backend should be testable in the terminal or the integrated dev environement of the framework used (if applicable). Example mastra has a dev studio that integrate a UI out of the box.
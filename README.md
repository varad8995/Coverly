<h1 align="center" id="title">🎨 Coverly — AI-Powered YouTube Thumbnail Generator</h1>

<p align="center"><img src="https://socialify.git.ci/varad8995/Coverly/image?custom_description=Generate+eye-catching+thumbnails+in+seconds%21+Using+AI+and+trending+design+insights%2C+Coverly+creates+thumbnails+optimized+for+clicks+%E2%80%94+just+give+it+a+title+or+reference+image%2C+and+watch+it+work+its+magic&amp;custom_language=Python&amp;description=1&amp;font=Jost&amp;language=1&amp;name=1&amp;owner=1&amp;pattern=Brick+Wall&amp;pulls=1&amp;stargazers=1&amp;theme=Dark" alt="project-image"></p>

<p id="description">Coverly is an AI-powered thumbnail generator designed specifically for YouTube creators. Upload an image enter your prompt and Coverly automatically predicts trending styles fetches inspiration from YouTube and generates stunning thumbnails using state-of-the-art AI models. 🚀 Built with LangGraph LLMs (OpenAI &amp; Gemini) Supabase Auth Redis + Valkey WebSockets Vercel &amp; AWS S3.</p>

  
  
<h2>🧐 Features</h2>

Here're some of the project's best features:

*   🎬 YouTube-Optimized Thumbnail Intelligence Detects YouTube as the target platform Scrapes trending thumbnails for visual reference Infers text style color palettes composition and font feel Mimics top-performing thumbnail patterns
*   🤖 Multi-Model AI Engine Choose between OpenAI (GPT-5) and Google Gemini Smart prompt refinement + creative enhancement Vision-based aesthetic/style extraction
*   🧠 LangGraph Powered Workflow Step-based AI pipeline for accuracy Auto-refine prompts if platform ≠ YouTube LangSmith for traceability & debugging Intelligent fallbacks + retry logic
*   📡 Real-Time Progress Streaming Redis + Valkey queue infrastructure Live job updates via WebSockets Real-time generation status + event stream
*   🔒 Modern Authentication Supabase Auth Google Login Secure session + user asset management
*   ☁️ Cloud Storage & CDN AWS S3 storage for images Fast delivery of generated assets

  
  
<h2>💻 Built with</h2>

Technologies used in the project:

*   Frontend Next.js — Application framework React — UI components TailwindCSS — Styling & design system WebSockets — Live thumbnail generation updates
*   AI & Workflows LangGraph — AI workflow orchestration LangSmith — Debugging tracing & monitoring OpenAI (GPT-5) — AI model option for generation Google Gemini — Alternative AI model option YouTube Content Scraper — Fetch trending thumbnail styles & formats Prompt Refinement Pipeline — Smart rewriting & enhancer chain
*   Backend / Realtime Redis — Job queue & temporary state Valkey — Pub/Sub for streaming progress FastApI— API routes for generation
*   Storage & Deployment AWS S3 — Image storage & CDN Vercel — Deployment & hosting Supabase — Auth & user management Google OAuth — Social login for creators

<h2>🛡️ License:</h2>

This project is licensed under the MIT

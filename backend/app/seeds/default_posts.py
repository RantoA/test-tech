# ruff: noqa: E501  (long prose strings)
"""Editorial articles published by default on a fresh installation."""

from typing import TypedDict


class SeedPost(TypedDict):
    slug: str
    title: str
    excerpt: str
    days_ago: int
    palette: tuple[str, str]
    content: list[dict[str, str]]


def _h(text: str) -> dict[str, str]:
    return {"type": "heading", "text": text}


def _s(text: str) -> dict[str, str]:
    return {"type": "subheading", "text": text}


def _p(text: str) -> dict[str, str]:
    return {"type": "paragraph", "text": text}


DEFAULT_POSTS: list[SeedPost] = [
    {
        "slug": "ai-agents-are-changing-everyday-software-work",
        "title": "AI agents are changing everyday software work",
        "excerpt": "From answering questions to completing multi-step tasks: how autonomous AI "
        "agents are moving into developer tools, support desks and back offices.",
        "days_ago": 1,
        "palette": ("#1e3a8a", "#93c5fd"),
        "content": [
            _p(
                "For a few years, most people met AI through a chat window: you ask, it answers. "
                "The new generation of tools goes one step further. AI agents receive a goal, "
                "split it into steps, call tools such as a code editor, a browser or an internal "
                "API, check the result and try again when something fails."
            ),
            _h("From assistants to agents"),
            _p(
                "The difference is autonomy. An assistant suggests the next line of code; an agent "
                "opens the project, runs the tests, edits several files and proposes a complete "
                "change for review. The human role shifts from typing to specifying, reviewing "
                "and deciding."
            ),
            _s("Where agents already help"),
            _p(
                "Software teams use them to fix small bugs, write tests and migrate code. Support "
                "teams use them to draft answers grounded in internal documentation. Operations "
                "teams use them to reconcile data between tools that were never designed to talk "
                "to each other."
            ),
            _h("What still needs a human"),
            _p(
                "Agents remain fallible. They can misunderstand an ambiguous request or confidently "
                "take a wrong path. Successful teams keep a clear review step, limit the "
                "permissions given to agents and log every action so that mistakes are easy to "
                "spot and undo."
            ),
        ],
    },
    {
        "slug": "small-language-models-when-smaller-is-better",
        "title": "Small language models: when smaller is better",
        "excerpt": "Compact models that run on a laptop or a phone are getting surprisingly good. "
        "Here is why many companies now pick the smallest model that does the job.",
        "days_ago": 3,
        "palette": ("#134e4a", "#5eead4"),
        "content": [
            _p(
                "Headlines usually focus on the largest AI models. Yet a quieter trend matters just "
                "as much for businesses: small language models, compact enough to run on a single "
                "server, a laptop or even a smartphone."
            ),
            _h("Why size matters"),
            _p(
                "Smaller models answer faster, cost less per request and can run without sending "
                "data to a third party. For tasks like classifying tickets, extracting fields from "
                "documents or summarizing short texts, they are often good enough."
            ),
            _s("Privacy and offline use"),
            _p(
                "Running a model locally keeps sensitive data inside the company network. It also "
                "makes features available offline, which is valuable for field teams, embedded "
                "devices and regions with unreliable connectivity."
            ),
            _h("Choosing the right model"),
            _p(
                "The practical rule is simple: start with a clear evaluation set, test a few model "
                "sizes and keep the smallest one that meets your quality bar. Larger models remain "
                "useful for complex reasoning, but they do not need to handle every request."
            ),
        ],
    },
    {
        "slug": "ai-regulation-what-businesses-should-prepare-for",
        "title": "AI regulation: what businesses should prepare for",
        "excerpt": "Governments are moving from principles to rules. Transparency, risk "
        "assessment and human oversight are becoming everyday obligations for AI products.",
        "days_ago": 6,
        "palette": ("#3f3f46", "#d4d4d8"),
        "content": [
            _p(
                "After years of guidelines and voluntary commitments, AI is entering the age of "
                "regulation. Several jurisdictions now follow a risk-based approach: the more an AI "
                "system can affect people's rights, safety or access to services, the stricter the "
                "requirements."
            ),
            _h("The common themes"),
            _s("Transparency"),
            _p(
                "Users should know when they interact with an AI system and when content has been "
                "generated by one. Clear labelling and documentation are becoming the norm."
            ),
            _s("Risk management and oversight"),
            _p(
                "High-impact uses, such as hiring, credit or healthcare, call for documented risk "
                "assessments, data quality controls and a meaningful way for humans to review or "
                "override automated decisions."
            ),
            _h("How to get ready"),
            _p(
                "A good first step is an inventory: list where AI is used, which data it relies on "
                "and who is accountable for each system. Companies that already track this "
                "information will find compliance far less painful than those starting from zero."
            ),
        ],
    },
    {
        "slug": "generative-ai-in-healthcare-promise-and-caution",
        "title": "Generative AI in healthcare: promise and caution",
        "excerpt": "Clinical notes, patient communication and research summaries are early use "
        "cases. Accuracy, privacy and accountability decide how far adoption can go.",
        "days_ago": 9,
        "palette": ("#7f1d1d", "#fca5a5"),
        "content": [
            _p(
                "Healthcare professionals spend a large share of their time on paperwork. "
                "Generative AI promises to give some of that time back, and hospitals around the "
                "world are running pilots to measure the real benefit."
            ),
            _h("Early use cases"),
            _p(
                "The most common experiments draft clinical notes from a consultation, prepare "
                "discharge summaries, translate medical jargon into plain language for patients and "
                "help researchers scan large volumes of scientific literature."
            ),
            _s("Keeping a clinician in the loop"),
            _p(
                "In every serious deployment, the AI drafts and a professional validates. Models "
                "can produce fluent but incorrect statements, so the final responsibility must "
                "stay with a qualified person."
            ),
            _h("The conditions for trust"),
            _p(
                "Patient data must be protected, results must be evaluated on realistic cases and "
                "errors must be reported and analysed. Progress will be steady rather than "
                "spectacular, and that is probably a good thing."
            ),
        ],
    },
    {
        "slug": "the-energy-cost-of-artificial-intelligence",
        "title": "The energy cost of artificial intelligence",
        "excerpt": "Training and running AI models consumes a growing amount of electricity and "
        "water. Efficiency is becoming a technical, economic and environmental priority.",
        "days_ago": 12,
        "palette": ("#365314", "#bef264"),
        "content": [
            _p(
                "Every AI answer runs on hardware in a data center somewhere. As usage grows, so "
                "does the demand for electricity and for the water used to cool these facilities. "
                "The topic has moved from research papers to boardroom discussions."
            ),
            _h("Training versus everyday use"),
            _p(
                "Training a large model is energy intensive, but it happens once. Serving millions "
                "of requests every day can end up consuming more over the lifetime of a model. "
                "This is why efficiency at inference time matters so much."
            ),
            _s("Levers for efficiency"),
            _p(
                "Smaller specialised models, better hardware, caching of frequent answers and "
                "scheduling heavy workloads when renewable energy is abundant all reduce the "
                "footprint without giving up useful features."
            ),
            _h("Measuring before optimizing"),
            _p(
                "Teams cannot improve what they do not measure. Tracking the energy and cost per "
                "request, and choosing the lightest model that meets the need, is quickly becoming "
                "part of responsible AI engineering."
            ),
        ],
    },
]

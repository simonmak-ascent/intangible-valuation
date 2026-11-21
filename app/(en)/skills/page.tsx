import fs from "node:fs";
import path from "node:path";

import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { Code, Calculator, BookOpen, Scale } from "lucide-react";

/**
 * Every skill lives as `skills/<slug>/SKILL.md` — the same files a reader copies into their
 * OpenCode skills directory. Until 2026-11-21 this page hard-coded a copy of their name, description
 * and "required MCP tools", and nothing read the files: editing a skill changed nothing a reader saw,
 * and the tool chips named *methods* (`relief_from_royalty`, `mpeem`) rather than the tools that serve
 * them. The page now reads the files at build time, so the file is the single source of truth.
 *
 * This is a server component and the page is prerendered, so the reads happen during `next build` —
 * the `skills/` tree does not need to ship in the runtime image.
 */
const ICONS: Record<string, typeof Calculator> = {
  "asset-valuation": Calculator,
  "discount-rate-construction": Code,
  "purchase-price-allocation": BookOpen,
  "impairment-testing": Scale,
};

type Skill = {
  slug: string;
  name: string;
  description: string;
  category: string;
  tools: string[];
  url: string;
};

function parseFrontMatter(text: string, slug: string): Skill {
  const match = /^---\n([\s\S]*?)\n---/.exec(text);
  const fields: Record<string, string> = {};
  for (const line of (match?.[1] ?? "").split("\n")) {
    const kv = /^([a-z_]+):\s*(.*)$/.exec(line.trim());
    if (kv) fields[kv[1]] = kv[2];
  }
  const tools = (fields.tools ?? "").replace(/^\[|\]$/g, "").split(",").map((t) => t.trim()).filter(Boolean);
  return {
    slug,
    name: fields.name ?? slug,
    description: fields.description ?? "",
    category: fields.category ?? "valuation",
    tools,
    url: `https://github.com/simonmak-ascent/intangible-valuation/blob/main/skills/${slug}/SKILL.md`,
  };
}

/**
 * The catalogue is the directory: a skill is a `skills/<slug>/SKILL.md`. A roster here would be a
 * second copy of the fact, and the first version of this page proved what that costs — the roster and
 * the files drifted, and nothing noticed.
 */
function loadSkills(): Skill[] {
  const dir = path.join(process.cwd(), "skills");
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && fs.existsSync(path.join(dir, entry.name, "SKILL.md")))
    .map((entry) => parseFrontMatter(fs.readFileSync(path.join(dir, entry.name, "SKILL.md"), "utf8"), entry.name))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export default function SkillsPage() {
  const skills = loadSkills();
  return (
    <div className="container-page py-12">
      <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "AI Skills" }]} />

      <div className="max-w-3xl mt-6 mb-12">
        <h1 className="text-display-sm text-primary-500 mb-4">AI Agent Skills</h1>
        <p className="text-lg text-neutral-500">
          OpenCode skills for domain-specific valuation workflows. Each skill defines a complete
          workflow with step-by-step instructions, required MCP tools, and expected outputs.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {skills.map((skill) => {
          const Icon = ICONS[skill.slug] ?? Calculator;
          return (
            <div key={skill.slug} className="card p-6 hover:shadow-elevation transition-all">
              <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center mb-4">
                <Icon className="w-5 h-5 text-primary-500" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-serif font-semibold text-neutral-900 dark:text-white">{skill.name}</h3>
                <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-500">
                  {skill.category}
                </span>
              </div>
              <p className="text-sm text-neutral-500 mb-4">{skill.description}</p>
              <div>
                <p className="text-xs font-semibold text-neutral-400 uppercase mb-2">Required MCP Tools</p>
                <div className="flex flex-wrap gap-1.5">
                  {skill.tools.map((tool) => (
                    <code key={tool} className="text-xs font-mono bg-neutral-100 dark:bg-neutral-800 px-1.5 py-0.5 rounded">
                      {tool}
                    </code>
                  ))}
                </div>
              </div>
              <a href={skill.url} className="mt-4 inline-block text-sm font-medium text-primary-500 hover:underline">
                Read SKILL.md
              </a>
            </div>
          );
        })}
      </div>

      <div className="mt-12 card p-6 text-center">
        <p className="text-sm text-neutral-500">
          To use a skill, copy its SKILL.md into your OpenCode skills directory and connect the MCP server.
        </p>
      </div>
    </div>
  );
}

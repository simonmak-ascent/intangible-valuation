import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { Code, Calculator, BookOpen, Scale } from "lucide-react";

const skills = [
  {
    icon: Calculator,
    name: "Asset Valuation",
    category: "valuation",
    description: "Comprehensive valuation workflow for any intangible asset type using all available methods.",
    path: "skills/asset-valuation/SKILL.md",
    tools: ["relief_from_royalty", "mpeem", "cost_approach", "market_approach"],
  },
  {
    icon: Code,
    name: "Discount Rate Construction",
    category: "valuation",
    description: "Build appropriate discount rates using CAPM, WACC, build-up method, and DLOM.",
    path: "skills/discount-rate-construction/SKILL.md",
    tools: ["capm", "wacc", "build_up_discount_rate"],
  },
  {
    icon: BookOpen,
    name: "Purchase Price Allocation",
    category: "workflow",
    description: "Complete PPA workflow following ASC 805/IFRS 3 with full waterfall calculation.",
    path: "skills/purchase-price-allocation/SKILL.md",
    tools: ["ppa_waterfall", "goodwill_calculation", "valuation_multiple_methods"],
  },
  {
    icon: Scale,
    name: "Impairment Testing",
    category: "compliance",
    description: "Goodwill and intangible asset impairment testing compliant with ASC 350/IAS 36.",
    path: "skills/impairment-testing/SKILL.md",
    tools: ["impairment_test", "fair_value_measurement", "recoverable_amount"],
  },
];

export default function SkillsPage() {
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
        {skills.map((skill) => (
          <div key={skill.name} className="card p-6 hover:shadow-elevation transition-all">
            <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center mb-4">
              <skill.icon className="w-5 h-5 text-primary-500" />
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
          </div>
        ))}
      </div>

      <div className="mt-12 card p-6 text-center">
        <p className="text-sm text-neutral-500">
          To use a skill, copy the SKILL.md file into your OpenCode skills directory and connect the MCP server.
        </p>
      </div>
    </div>
  );
}

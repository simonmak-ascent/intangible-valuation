// Locale registry + landing copy for the intangible-valuation frontage.
// Locales mirror the Ascent Partners site: en (default, no prefix), zh (/zh), hk (/hk).

export const locales = ["en", "zh", "hk"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

export const LOCALE_META: Record<Locale, { htmlLang: string; label: string; prefix: string }> = {
  en: { htmlLang: "en-GB", label: "English", prefix: "" },
  zh: { htmlLang: "zh-Hans", label: "中文", prefix: "/zh" },
  hk: { htmlLang: "zh-Hant-HK", label: "繁體", prefix: "/hk" },
};

export function isLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}

export function hrefFor(locale: Locale, path: string): string {
  const clean = path === "/" ? "" : path.startsWith("/") ? path : `/${path}`;
  return `${LOCALE_META[locale].prefix}${clean}` || "/";
}

const ENDPOINT = "https://intangible-valuation.simonmak.com/api/mcp";
const REGISTRY = "io.github.simonmak-ascent/intangible-valuation";

export interface LandingCopy {
  type: string;
  name: string;
  value: string;
  thesis: string;
  stats: { value: string; label: string }[];
  capsHeading: string;
  capabilities: string[];
  standardsHeading: string;
  standards: string[];
  connectHeading: string;
  connectIntro: string;
  factsHeading: string;
  facts: { label: string; value: string; code?: boolean }[];
  originHeading: string;
  originBody: string;
  techLink: string;
  contact: string;
  docs: string;
  source: string;
  back: string;
  copy: string;
  copied: string;
  crumbHome: string;
  crumbTools: string;
  langLabel: string;
}

export const LANDING_COPY: Record<Locale, LandingCopy> = {
  en: {
    type: "MCP server + REST API",
    name: "Intangible Asset Valuation",
    value: "Value IP, technology, customer and goodwill assets for PPA, impairment and royalty workflows.",
    thesis: "Price the assets a balance sheet cannot see — and show the working, to the standard an auditor will test.",
    stats: [
      { value: "14", label: "MCP tools" },
      { value: "124+", label: "formulas" },
      { value: "ASC · IFRS", label: "cited standards" },
      { value: "Open", label: "no API key" },
    ],
    capsHeading: "Capabilities",
    capabilities: [
      "14 tools / 124+ formulas",
      "Relief-from-royalty, MPEEM, incremental cash flow",
      "ASC 805 / IFRS 3 PPA; ASC 350 / IAS 36 impairment",
      "Auditable: every result carries its formula, assumptions and steps",
    ],
    standardsHeading: "Standards",
    standards: ["ASC 805", "IFRS 3", "ASC 350", "IAS 36"],
    connectHeading: "Connect",
    connectIntro: "Point an MCP client at the hosted endpoint. Open access, no API key.",
    factsHeading: "Facts",
    facts: [
      { label: "Endpoint", value: ENDPOINT, code: true },
      { label: "Transport", value: "Streamable HTTP" },
      { label: "Auth", value: "Open — no API key" },
      { label: "Licence", value: "MIT" },
      { label: "Registry", value: REGISTRY, code: true },
    ],
    originHeading: "Where it comes from",
    originBody: "Built by the Ascent Partners technology practice from the Intangible Asset Valuation textbook — the method, opened for inspection.",
    techLink: "Technology Advisory",
    contact: "Contact us",
    docs: "Documentation",
    source: "Source",
    back: "All tools",
    copy: "Copy",
    copied: "Copied",
    crumbHome: "Home",
    crumbTools: "Open Tooling",
    langLabel: "Language",
  },
  zh: {
    type: "MCP 服务器 + REST API",
    name: "Intangible Asset Valuation",
    value: "为收购价分摊、减值及权利金场景评估知识产权、技术、客户及商誉资产。",
    thesis: "为资产负债表看不见的资产定价——并摊开推理过程，对齐核数师将检验的准则。",
    stats: [
      { value: "14", label: "个 MCP 工具" },
      { value: "124+", label: "个公式" },
      { value: "ASC · IFRS", label: "引用准则" },
      { value: "开放", label: "无需密钥" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 个工具 / 124+ 公式",
      "权利金节省法、MPEEM、增量现金流",
      "ASC 805 / IFRS 3 收购价分摊；ASC 350 / IAS 36 减值",
      "可审计：每项结果附带其公式、假设与步骤",
    ],
    standardsHeading: "准则",
    standards: ["ASC 805", "IFRS 3", "ASC 350", "IAS 36"],
    connectHeading: "连接",
    connectIntro: "将 MCP 客户端指向托管端点。开放访问，无需 API 密钥。",
    factsHeading: "信息",
    facts: [
      { label: "端点", value: ENDPOINT, code: true },
      { label: "传输", value: "Streamable HTTP" },
      { label: "认证", value: "开放——无需密钥" },
      { label: "许可", value: "MIT" },
      { label: "注册表", value: REGISTRY, code: true },
    ],
    originHeading: "来源",
    originBody: "由艾升集团技术咨询团队依据《无形资产估值》教材构建——将方法开放以供检视。",
    techLink: "技术咨询",
    contact: "联系我们",
    docs: "文档",
    source: "源代码",
    back: "全部工具",
    copy: "复制",
    copied: "已复制",
    crumbHome: "首页",
    crumbTools: "开放工具",
    langLabel: "语言",
  },
  hk: {
    type: "MCP 伺服器 + REST API",
    name: "Intangible Asset Valuation",
    value: "為收購價分攤、減值及權利金場景評估知識產權、技術、客戶及商譽資產。",
    thesis: "為資產負債表看不見的資產定價——並攤開推理過程，對齊核數師將檢驗的準則。",
    stats: [
      { value: "14", label: "個 MCP 工具" },
      { value: "124+", label: "個公式" },
      { value: "ASC · IFRS", label: "引用準則" },
      { value: "開放", label: "無需密鑰" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 個工具 / 124+ 公式",
      "權利金節省法、MPEEM、增量現金流",
      "ASC 805 / IFRS 3 收購價分攤；ASC 350 / IAS 36 減值",
      "可審計：每項結果附帶其公式、假設與步驟",
    ],
    standardsHeading: "準則",
    standards: ["ASC 805", "IFRS 3", "ASC 350", "IAS 36"],
    connectHeading: "連接",
    connectIntro: "將 MCP 客戶端指向託管端點。開放存取，無需 API 密鑰。",
    factsHeading: "資訊",
    facts: [
      { label: "端點", value: ENDPOINT, code: true },
      { label: "傳輸", value: "Streamable HTTP" },
      { label: "認證", value: "開放——無需密鑰" },
      { label: "授權", value: "MIT" },
      { label: "註冊表", value: REGISTRY, code: true },
    ],
    originHeading: "來源",
    originBody: "由艾升集團技術諮詢團隊依據《無形資產估值》教材構建——將方法開放以供檢視。",
    techLink: "技術諮詢",
    contact: "聯絡我們",
    docs: "文件",
    source: "原始碼",
    back: "全部工具",
    copy: "複製",
    copied: "已複製",
    crumbHome: "首頁",
    crumbTools: "開放工具",
    langLabel: "語言",
  },
};

export interface ConnectClient {
  key: string;
  label: string;
  code: string;
}

export function connectClients(): ConnectClient[] {
  const key = "intangible-valuation";
  const json = (o: unknown) => JSON.stringify(o, null, 2);
  const servers = json({ mcpServers: { [key]: { url: ENDPOINT } } });
  return [
    { key: "opencode", label: "OpenCode", code: json({ $schema: "https://opencode.ai/config.json", mcp: { [key]: { type: "remote", url: ENDPOINT } } }) },
    { key: "claude-code", label: "Claude Code", code: `claude mcp add --transport http ${key} ${ENDPOINT}` },
    { key: "claude-desktop", label: "Claude Desktop", code: servers },
    { key: "cursor", label: "Cursor", code: servers },
    { key: "vscode", label: "VS Code", code: json({ servers: { [key]: { type: "http", url: ENDPOINT } } }) },
    { key: "generic", label: "Any MCP client", code: servers },
  ];
}

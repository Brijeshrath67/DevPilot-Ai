import { useMemo, useState } from "react";
import { FlaskConical } from "lucide-react";
import type { GeneratedTest } from "../../types/api";
import { Tabs } from "../ui/Tabs";
import { CodeViewer } from "../ui/CodeViewer";
import { titleCase } from "../../lib/utils";

export interface GeneratedTestPanelProps {
  tests: GeneratedTest[];
}

export function GeneratedTestPanel({ tests }: GeneratedTestPanelProps) {
  const [active, setActive] = useState(0);

  const tabs = useMemo(
    () =>
      tests.map((test) => ({
        id: test.type,
        label: titleCase(test.type).replace("_", " "),
      })),
    [tests]
  );

  const current = tests[Math.min(active, tests.length - 1)];

  if (tests.length === 0) {
    return (
      <div className="rounded-xl border border-line-1 bg-panel-2 px-5 py-8 text-center">
        <div className="mx-auto mb-2 grid h-10 w-10 place-items-center rounded-full bg-accent/10 text-accent">
          <FlaskConical className="h-4 w-4" />
        </div>
        <p className="text-sm font-medium text-ink">No tests generated</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl2 border border-line-1 bg-panel-2">
      <div className="border-b border-line-1 px-4 py-2.5">
        <Tabs
          tabs={tabs}
          active={tabs[Math.min(active, tabs.length - 1)]?.id ?? ""}
          onChange={(v) => setActive(tabs.findIndex((t) => t.id === v))}
        />
      </div>
      {current && <CodeViewer code={current.content} filename={current.type} />}
    </div>
  );
}

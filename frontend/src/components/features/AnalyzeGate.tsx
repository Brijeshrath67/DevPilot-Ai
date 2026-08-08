import { Link } from "react-router-dom";
import { ArrowRight, ScanSearch } from "lucide-react";
import { EmptyState } from "../ui/EmptyState";
import { Button } from "../ui/Button";

export interface AnalyzeGateProps {
  repoId: string | number;
  title?: string;
  description?: string;
}

export function AnalyzeGate({
  repoId,
  title = "Repository not analyzed yet",
  description = "Analyze the repository to unlock code review, security audits, documentation, tests, and the QA assistant.",
}: AnalyzeGateProps) {
  return (
    <EmptyState
      icon={<ScanSearch className="h-5 w-5" />}
      title={title}
      description={description}
      action={
        <Link to={`/repo/${repoId}`}>
          <Button size="sm" icon={<ArrowRight className="h-3.5 w-3.5" />}>
            Go to overview
          </Button>
        </Link>
      }
    />
  );
}

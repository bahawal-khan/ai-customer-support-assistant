"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { AlertTriangle, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { StepIndicator, type ComplaintStep } from "@/features/complaint/step-indicator";
import { Examples } from "@/features/complaint/examples";
import { AttachmentArea } from "@/features/complaint/attachment-area";
import { PipelineStages } from "@/features/complaint/pipeline-stages";
import { analyzeComplaint } from "@/lib/api/client";
import { MAX_COMPLAINT_LENGTH } from "@/lib/constants";
import { ApiError } from "@/types/api";

export function NewComplaintView() {
  const router = useRouter();
  const [text, setText] = React.useState("");
  const [files, setFiles] = React.useState<File[]>([]);
  const [step, setStep] = React.useState<ComplaintStep>(0);
  const [error, setError] = React.useState<string | null>(null);

  const trimmed = text.trim();
  const isValid = trimmed.length > 0 && trimmed.length <= MAX_COMPLAINT_LENGTH;

  async function handleAnalyze() {
    if (!isValid) return;
    setError(null);
    setStep(1);

    try {
      const result = await analyzeComplaint(trimmed);
      router.push(`/complaints/${result.complaint_id}`);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong while analyzing this complaint. Please try again."
      );
      setStep(0);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New Complaint</h1>
        <p className="text-sm text-muted-foreground">
          Describe the issue in your own words — our AI will classify it and find a grounded answer.
        </p>
      </div>

      <StepIndicator current={step} />

      {step === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle>Describe the issue</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  <AlertTriangle className="size-4 shrink-0" />
                  {error}
                </div>
              )}

              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="e.g. My order arrived damaged and I'd like a replacement..."
                rows={6}
                maxLength={MAX_COMPLAINT_LENGTH}
                aria-label="Complaint description"
              />
              <div className="flex justify-end text-xs text-muted-foreground">
                {trimmed.length}/{MAX_COMPLAINT_LENGTH}
              </div>

              <div>
                <p className="mb-2 text-xs font-medium text-muted-foreground">Try an example</p>
                <Examples onSelect={setText} />
              </div>

              <AttachmentArea files={files} onChange={setFiles} />

              <Button className="w-full" disabled={!isValid} onClick={handleAnalyze}>
                <Sparkles className="size-4" />
                Analyze Complaint
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {step === 1 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle>Analyzing your complaint</CardTitle>
            </CardHeader>
            <CardContent>
              <PipelineStages />
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

"use client";

import { motion, useReducedMotion } from "motion/react";
import { Bot, Copy } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function ResponseCard({ response }: { response: string | null }) {
  const prefersReducedMotion = useReducedMotion();

  async function handleCopy() {
    if (!response) return;
    try {
      await navigator.clipboard.writeText(response);
      toast.success("Response copied to clipboard");
    } catch {
      toast.error("Couldn't copy to clipboard");
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      transition={{ duration: 0.28, delay: 0.35, ease: "easeOut" }}
    >
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Avatar size="sm">
              <AvatarFallback className="bg-primary/15 text-primary">
                <Bot className="size-4" />
              </AvatarFallback>
            </Avatar>
            Response
          </CardTitle>
          <div className="flex items-center gap-1.5">
            <Button variant="outline" size="sm" onClick={handleCopy} disabled={!response}>
              <Copy className="size-3.5" />
              Copy
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {response ? (
            <motion.p
              key={response}
              initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="text-sm leading-relaxed whitespace-pre-wrap"
            >
              {response}
            </motion.p>
          ) : (
            <p className="text-sm text-muted-foreground">
              No response was generated for this complaint. The knowledge base may not have had enough
              information to answer confidently.
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

/**
 * AI Assistant component for Smart CRM SaaS application.
 * Provides UI to interact with backend AI assistant API for:
 * - Message summaries
 * - Follow-up reminders
 * - Invoice text generation
 */

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useMutation } from "@tanstack/react-query";
import { sendAIPrompt } from "@/lib/api/ai";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

export function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const { mutate, isPending } = useMutation({
    mutationFn: sendAIPrompt,
    onSuccess: (data) => {
      setResponse(data.response);
    },
    onError: () => {
      toast.error("Failed to get AI response");
    },
  });

  const handleSubmit = () => {
    if (!prompt.trim()) return;
    mutate({ prompt });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="secondary"
          className="fixed bottom-6 right-6 rounded-full shadow-lg h-14 w-14"
          size="icon"
        >
          <span className="text-xl">AI</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>AI Assistant</DialogTitle>
        </DialogHeader>
        <div className="flex-1 flex flex-col gap-4">
          <div className="flex-1 bg-muted/50 p-4 rounded-lg overflow-auto">
            {response ? (
              <div className="prose dark:prose-invert max-w-none">
                {response}
              </div>
            ) : (
              <div className="text-muted-foreground text-center py-8">
                {isPending ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                ) : (
                  "Ask me anything about your clients, projects, or data"
                )}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask me anything..."
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <Button onClick={handleSubmit} disabled={isPending}>
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Send"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
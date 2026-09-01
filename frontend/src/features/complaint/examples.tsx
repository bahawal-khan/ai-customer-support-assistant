const EXAMPLES = [
  "My package says delivered but I never received it.",
  "I was charged twice for the same order and need this fixed.",
  "My router keeps dropping the Wi-Fi connection every hour.",
  "I'd like to cancel my subscription before it renews.",
];

export function Examples({ onSelect }: { onSelect: (text: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {EXAMPLES.map((example) => (
        <button
          key={example}
          type="button"
          onClick={() => onSelect(example)}
          className="rounded-full border border-border bg-muted/50 px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
        >
          {example}
        </button>
      ))}
    </div>
  );
}

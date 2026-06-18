import { useEffect, useRef, useState } from "react";
import { ArrowUp, Mic, Paperclip, Square } from "lucide-react";

type Props = {
  onSend: (text: string) => void;
  disabled?: boolean;
};

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    taRef.current?.focus();
  }, []);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  }, [value]);

  const submit = () => {
    const v = value.trim();
    if (!v || disabled) return;
    onSend(v);
    setValue("");
    requestAnimationFrame(() => taRef.current?.focus());
  };

  return (
    <div className="relative">
      <div className="glass-strong flex items-end gap-2 rounded-2xl p-2 shadow-[0_-10px_40px_-20px_var(--color-primary)]">
        <button
          type="button"
          className="grid h-9 w-9 shrink-0 place-items-center rounded-xl text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          aria-label="Attach"
          title="Attach document (coming soon)"
        >
          <Paperclip className="h-4 w-4" />
        </button>

        <textarea
          ref={taRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={1}
          placeholder="Ask a question about any topic…"
          className="flex-1 resize-none bg-transparent px-1 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          style={{ maxHeight: 200 }}
        />

        <button
          type="button"
          className="grid h-9 w-9 shrink-0 place-items-center rounded-xl text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          aria-label="Voice input"
        >
          <Mic className="h-4 w-4" />
        </button>

        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send"
          className="grid h-9 w-9 shrink-0 place-items-center rounded-xl brand-gradient text-white shadow-[0_8px_24px_-8px_var(--color-primary)] transition-all hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
        >
          {disabled ? <Square className="h-3.5 w-3.5" /> : <ArrowUp className="h-4 w-4" />}
        </button>
      </div>
      <p className="mt-2 text-center text-[10px] text-muted-foreground">
        Wikipedia Research Assistant can make mistakes. Verify with the cited articles.
      </p>
    </div>
  );
}

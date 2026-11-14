import { render } from "@testing-library/react";
import { fireEvent, screen } from "@testing-library/dom";
import { describe, expect, it, vi } from "vitest";
import { Badge, Button, Card } from "../components/ui";
import { BilingualLessonContent } from "../components/translation";
import { LessonContent, parseLessonContent } from "../components/lesson-content";

describe("shared UI", () => {
  it("renders common controls", () => {
    render(<Card><Badge>Beginner</Badge><Button>Start learning</Button></Card>);
    expect(screen.getByText("Beginner")).toBeVisible();
    expect(screen.getByRole("button", { name: "Start learning" })).toBeEnabled();
  });

  it("toggles and persists Myanmar explanations", () => {
    render(<BilingualLessonContent english="English explanation" myanmar="မြန်မာရှင်းလင်းချက်" />);
    expect(screen.queryByText("မြန်မာရှင်းလင်းချက်")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show MM" }));
    expect(screen.getByText("မြန်မာရှင်းလင်းချက်")).toBeVisible();
    expect(localStorage.getItem("showMyanmar")).toBe("true");
  });

  it("parses authored lesson sections, lists, and fenced code", () => {
    const blocks = parseLessonContent("Introduction\nWelcome.\n\nLearning objectives\n- Read code\n- Run code\n\nComplete C program — demo\n```c\nint main(void) { return 0; }\n```\n\nExpected output\n```text\nOK\n```");
    expect(blocks.filter(block => block.kind === "heading").map(block => block.kind === "heading" ? block.text : "")).toContain("Complete C program — demo");
    expect(blocks.filter(block => block.kind === "list")).toHaveLength(1);
    expect(blocks.filter(block => block.kind === "code")).toHaveLength(2);
  });

  it("renders lesson content and copies code snippets", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    render(<LessonContent content={"Introduction\nWelcome to the lesson.\n\nLearning objectives\n- Read code\n- Run code\n\nComplete C program — demo\n```c\n#include <stdio.h>\nint main(void) { return 0; }\n```\n\nExpected output\n```text\nOK\n```"} />);
    expect(screen.getByRole("heading", { name: "Introduction" })).toBeVisible();
    expect(screen.getByText("Read code")).toBeVisible();
    expect(screen.getAllByText("Expected output").length).toBeGreaterThan(0);
    fireEvent.click(screen.getAllByRole("button", { name: "Copy code" })[0]);
    expect(await screen.findByRole("button", { name: "Code copied" })).toBeVisible();
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining("int main"));
  });
});

import { cleanup, render } from "@testing-library/react";
import { fireEvent, screen } from "@testing-library/dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Badge, Button, Card } from "../components/ui";
import { BilingualLessonContent } from "../components/translation";
import { LessonContent, parseLessonContent } from "../components/lesson-content";

afterEach(cleanup);

describe("shared UI", () => {
  it("renders common controls", () => {
    render(<Card><Badge>Beginner</Badge><Button>Start learning</Button></Card>);
    expect(screen.getByText("Beginner")).toBeVisible();
    expect(screen.getByRole("button", { name: "Start learning" })).toBeEnabled();
  });

  it("renders the requested lesson language", () => {
    const view = render(<BilingualLessonContent english="English explanation" myanmar="မြန်မာရှင်းလင်းချက်" locale="my" />);
    expect(screen.getByText("မြန်မာရှင်းလင်းချက်")).toBeVisible();
    expect(screen.queryByText("English explanation")).not.toBeInTheDocument();
    view.rerender(<BilingualLessonContent english="English explanation" myanmar="မြန်မာရှင်းလင်းချက်" />);
    expect(screen.getByText("English explanation")).toBeVisible();
  });

  it("parses authored lesson sections, lists, and fenced code", () => {
    const blocks = parseLessonContent("Introduction\nWelcome.\n\nLearning objectives\n- Read code\n- Run code\n\nComplete C program — demo\n```c\nint main(void) { return 0; }\n```\n\nExpected output\n```text\nOK\n```");
    expect(blocks.filter(block => block.kind === "heading").map(block => block.kind === "heading" ? block.text : "")).toContain("Complete C program — demo");
    expect(blocks.filter(block => block.kind === "list")).toHaveLength(1);
    expect(blocks.filter(block => block.kind === "code")).toHaveLength(2);
  });

  it("keeps Burmese explanation sections in the rendered lesson", () => {
    render(<LessonContent content={"Introduction\nEnglish content\n\nMyanmar explanation\nမြန်မာအကြောင်းအရာ အပြည့်အစုံ"} />);
    expect(screen.getByText("မြန်မာအကြောင်းအရာ အပြည့်အစုံ")).toBeVisible();
  });

  it("can remove legacy Burmese sections from the English lesson", () => {
    render(<LessonContent content={"Introduction\nEnglish content\n\nMyanmar explanation\nမြန်မာအကြောင်းအရာ"} excludeSections={["Myanmar explanation"]} />);
    expect(screen.getByText("English content")).toBeVisible();
    expect(screen.queryByText("မြန်မာအကြောင်းအရာ")).not.toBeInTheDocument();
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

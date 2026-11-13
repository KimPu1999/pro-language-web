import { render } from "@testing-library/react";
import { fireEvent, screen } from "@testing-library/dom";
import { describe, expect, it } from "vitest";
import { Badge, Button, Card } from "../components/ui";
import { BilingualLessonContent } from "../components/translation";

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
});

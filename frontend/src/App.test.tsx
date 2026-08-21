import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { CalendarView, DailyReviewForm, StatCard, TodoCard } from "./components";

describe("core UI", () => {
  it("renders a statistic card", () => {
    render(<BrowserRouter><StatCard label="Current streak" value="3 days" /></BrowserRouter>);
    expect(screen.getByText("Current streak")).toBeInTheDocument();
    expect(screen.getByText("3 days")).toBeInTheDocument();
  });

  it("renders calendar days and selects a date", () => {
    let selected = "";
    render(<CalendarView calendar={{ year: 2026, month: 8, days: [{ date: "2026-08-01", todo_count: 1, pending_count: 1, completed_count: 0, missed_count: 0 }] }} selectedDate="2026-08-01" onSelect={value => { selected = value; }} />);
    const dayLabels = screen.getAllByText("1");
    expect(dayLabels[0]).toBeInTheDocument();
    dayLabels[0].click();
    expect(selected).toBe("2026-08-01");
  });

  it("requires truthful confirmation before completing a Todo", () => {
    let completed = false;
    render(<TodoCard todo={{ id: "1", title: "Ship it", description: null, scheduled_date: "2026-08-21", original_scheduled_date: "2026-08-21", priority: "high", status: "pending", created_at: "", updated_at: "", completed_at: null, missed_at: null, miss_reason: null, carry_forward_count: 0, carry_forward_bonus_awarded: false }} onComplete={() => { completed = true; }} onMiss={() => {}} onEdit={() => {}} onDelete={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Complete" }));
    expect(screen.getByText("Did you actually complete this Todo?")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Yes, I completed it" }));
    expect(completed).toBe(true);
  });

  it("collects a structured miss reason and warns about the penalty", () => {
    let result = "";
    render(<TodoCard todo={{ id: "2", title: "Miss it", description: null, scheduled_date: "2026-08-21", original_scheduled_date: "2026-08-21", priority: "medium", status: "pending", created_at: "", updated_at: "", completed_at: null, missed_at: null, miss_reason: null, carry_forward_count: 0, carry_forward_bonus_awarded: false }} onComplete={() => {}} onMiss={(reason, code) => { result = `${code}:${reason}`; }} onEdit={() => {}} onDelete={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Miss" }));
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "poor_planning" } });
    expect(screen.getByText("This will cost you 7 points.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Confirm miss" }));
    expect(result).toBe("poor_planning:Poor planning");
  });

  it("submits the optional Daily Review form", () => {
    let saved = false;
    render(<DailyReviewForm review={{ id: null, review_date: "2026-08-21", mood_score: null, went_well: null, improvement: null, stats: { review_date: "2026-08-21", planned: 2, completed: 2, missed: 0, carried_forward: 0, pending: 0, resolved: 2, completion_rate: 1, successful: true, neutral: false } }} onSave={() => { saved = true; }} />);
    fireEvent.click(screen.getByRole("button", { name: "4" }));
    fireEvent.click(screen.getByRole("button", { name: "Finish day" }));
    expect(saved).toBe(true);
  });
});

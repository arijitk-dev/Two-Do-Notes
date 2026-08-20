import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { CalendarView, StatCard } from "./components";

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
});

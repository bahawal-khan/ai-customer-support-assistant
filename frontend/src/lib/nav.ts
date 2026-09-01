import type { LucideIcon } from "lucide-react";
import { BookOpen, History, LayoutDashboard, MessageSquarePlus } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/complaints/new", label: "New Complaint", icon: MessageSquarePlus },
  { href: "/history", label: "History", icon: History },
  { href: "/knowledge-base", label: "Knowledge Base", icon: BookOpen },
];

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Description: Merge class names with Tailwind conflict resolution.
 * Parameters:
 *   inputs: Class name values.
 * Returns:
 *   string: Merged class string.
 * Usage Example:
 *   const classes = cn("text-sm", isActive && "text-mint");
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

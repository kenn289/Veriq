import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

/**
 * Description: Generate button class names for variants and sizes.
 * Parameters:
 *   options: Variant and size options for the button.
 * Returns:
 *   string: Tailwind class list.
 * Usage Example:
 *   const classes = buttonVariants({ variant: "outline" });
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-full text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-mint text-ink hover:bg-mint/90 focus-visible:ring-mint",
        outline: "border border-paper/20 text-paper hover:border-mint/60 focus-visible:ring-mint",
      },
      size: {
        default: "h-11 px-6",
        sm: "h-9 px-4",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

/**
 * Description: Render a styled button component.
 * Parameters:
 *   props: Button props including variant and size.
 * Returns:
 *   JSX.Element: Styled button element.
 * Usage Example:
 *   <Button variant="outline">Learn more</Button>
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  ),
);

Button.displayName = "Button";

export { Button, buttonVariants };

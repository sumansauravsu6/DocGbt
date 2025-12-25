/**
 * Sign-in button component.
 */
import { SignInButton as ClerkSignInButton } from '@clerk/clerk-react';

export const SignInButton: React.FC = () => {
  return (
    <ClerkSignInButton mode="modal">
      <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:opacity-90 transition-opacity">
        Sign In
      </button>
    </ClerkSignInButton>
  );
};

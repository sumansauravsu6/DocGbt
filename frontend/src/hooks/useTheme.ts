/**
 * Custom hook for theme management.
 */
import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';

export const useTheme = () => {
  const { theme, toggleTheme, setTheme } = useAppStore();

  useEffect(() => {
    // Apply theme on mount
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  return {
    theme,
    toggleTheme,
    setTheme,
    isDark: theme === 'dark',
  };
};

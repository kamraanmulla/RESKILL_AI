import { Capacitor } from '@capacitor/core';
import { Browser } from '@capacitor/browser';

/**
 * Opens an external URL safely across platforms:
 * - Mobile (Android/iOS): Uses Capacitor Browser (Chrome Custom Tabs) for seamless viewing and easy return to the app
 * - Web (Desktop/Laptop): Uses window.open with noopener and noreferrer
 */
export async function openExternalUrl(url: string): Promise<void> {
  if (!url) return;

  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      console.warn('Blocked non-http(s) URL:', url);
      return;
    }

    if (Capacitor.isNativePlatform()) {
      await Browser.open({
        url,
        windowName: '_blank',
        presentationStyle: 'popover',
        toolbarColor: '#163626'
      });
    } else {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  } catch (error) {
    console.warn('Failed to open URL via Browser plugin, falling back to window.open', error);
    try {
      window.open(url, '_blank', 'noopener,noreferrer');
    } catch {
      // Ignored
    }
  }
}

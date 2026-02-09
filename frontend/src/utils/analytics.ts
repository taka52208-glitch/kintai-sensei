/**
 * Google Analytics 4 ユーティリティ
 * GA_IDが設定されている場合のみ動作
 */

import { config } from '../config';

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
    dataLayer: unknown[];
  }
}

let initialized = false;

/** GA4スクリプトを動的に読み込み */
export function initGA() {
  if (initialized || !config.gaId) return;

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${config.gaId}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag(...args: unknown[]) {
    window.dataLayer.push(args);
  };
  window.gtag('js', new Date());
  window.gtag('config', config.gaId, {
    send_page_view: false, // SPAなのでルーター側で送る
  });

  initialized = true;
}

/** ページビュー送信 */
export function trackPageView(path: string) {
  if (!config.gaId || !initialized) return;
  window.gtag('event', 'page_view', {
    page_path: path,
  });
}

/** カスタムイベント送信 */
export function trackEvent(name: string, params?: Record<string, string | number>) {
  if (!config.gaId || !initialized) return;
  window.gtag('event', name, params);
}

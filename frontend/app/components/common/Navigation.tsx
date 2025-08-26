'use client'

import React from 'react'
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import styles from '../../css/Navigation.module.css';

export default function Navigation() {
  const pathname = usePathname();
  const { user, isLoaded } = useUser();

  const userId = user?.id;

  // ユーザー情報がなければ何も表示しない
  if (!user) {
    return null;
  }

  // 環境変数から管理者メールアドレスを取得
  const adminEmail = process.env.NEXT_PUBLIC_ADMIN_EMAIL;

  const navLinks = [
    { name: 'トレンド', href: '/debates' },
    { name: '履歴', href: `/users/${userId}/history` },
    { name: 'プロフィール', href: `/users/${userId}` },
  ];

  if (!isLoaded || !user) {
    // ローディング中のスケルトンUIなどを表示すると、さらに親切です
    return <nav className={styles.navContainer}></nav>;
  }
  return (
    <nav className={styles.navContainer}>
      {navLinks.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.name}
            href={link.href}
            className={isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}
          >
            {link.name}
          </Link>
        );
      })}
      {/* 管理者メールアドレスが一致する場合のみ「管理者機能」タブを表示 */}
      {user.primaryEmailAddress?.emailAddress === adminEmail && (
        <Link
          href="/admin"
          className={pathname === '/admin' ? `${styles.navLink} ${styles.active}` : styles.navLink}
        >
          管理者機能
        </Link>
      )}
    </nav>
  )
}

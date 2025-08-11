'use client'

import Link from 'next/link'
import React from 'react'
import { SignedIn, UserButton } from "@clerk/nextjs";

export default function Header() {
    return (
        <header className='header'>

            <Link href="/debates" className='hanten-logo'>
                Hanten
            </Link>

            {/* 右側のボタンをまとめるdiv */}
            <div className="header-actions">
                <SignedIn>
                    <Link href="/create" className="create-button">
                        新規作成
                    </Link>
                    <UserButton
                        appearance={{
                            elements: {
                                avatarBox: {
                                    width: '35px',
                                    height: '35px',
                                }
                            }
                        }}
                    />
                </SignedIn>
            </div>
        </header>
    )
}

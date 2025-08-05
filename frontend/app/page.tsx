import Image from "next/image";
import styles from "./page.module.css";
import { SignInButton } from "@clerk/nextjs";
import Link from "next/link";

export default function Home() {
  return (
    <div>
        このアプリはリバースディベートを行うアプリです。
        <Link href={'/sign-in'}>
          サインイン
        </Link>
        <br></br>
        <Link href={'/sign-up'}>
          サインアップ
        </Link>
    </div>
  );
}

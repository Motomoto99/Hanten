import Link from "next/link";

export default function Home() {
  return (
    <div className="sign">
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

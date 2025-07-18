'use client'

import React from 'react'
import axios from 'axios'
import { useEffect, useState } from 'react'

export default function page() {
    const [data, setData] = useState({message: ''})

    useEffect(() => {
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/testapi/backend/`)
            .then((res) => res.data)
            .then((data) => {
                setData(data)
            })
    },[])
    return (
        <div>
            Hello, Next.js
            <div>こんにちは、{data.message}!</div>
        </div>

    )
}

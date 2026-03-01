'use client';

import React from 'react'
import Settings from '@/components/component/settings'
import Link from "next/link"


import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuItem } from "@/components/ui/dropdown-menu"



const page = () => {
    return (
        <div>
            <header className="flex items-center h-16 px-4 border-b shrink-0 md:px-6">
        <Link href="#" className="flex items-center gap-2 text-lg font-semibold sm:text-base mr-4" prefetch={false}>
          <div className="w-6 h-6" />
          <span className="sr-only">Anomaly Detection Dashboard</span>
        </Link>
        <nav className="hidden font-medium sm:flex flex-row items-center gap-5 text-sm lg:gap-6">
          <Link href="/" className="font-bold" prefetch={false}>
            Dashboard
          </Link>
        
          <Link href="/reports" className="text-muted-foreground" prefetch={false}>
            Reports
          </Link>
          <Link href="/globasetting" className="text-muted-foreground" prefetch={false}>
            Settings
          </Link>
        </nav>
     
      </header>
            <Settings></Settings>
        </div>
    )
}

export default page

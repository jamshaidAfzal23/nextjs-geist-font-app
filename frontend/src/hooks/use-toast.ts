'use client'

import { useCallback } from 'react'

type ToastType = 'success' | 'error' | 'info' | 'warning'

interface ToastOptions {
  title?: string
  description?: string
  type?: ToastType
  duration?: number
}

export function useToast() {
  const toast = useCallback(({ title, description, type = 'info', duration = 3000 }: ToastOptions) => {
    // For now, we'll use console.log as a placeholder
    // In a real application, you would integrate with a toast library
    console.log(`Toast: ${type} - ${title}\n${description}`)
  }, [])

  return { toast }
}
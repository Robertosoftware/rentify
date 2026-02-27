export interface User {
  id: string
  email: string
  full_name: string | null
  auth_provider: string
  subscription_status: 'none' | 'trialing' | 'active' | 'past_due' | 'canceled'
  trial_ends_at: string | null
  telegram_chat_id: string | null
  is_admin: boolean
  gdpr_consent_at: string | null
  created_at: string
}

export interface Preference {
  id: string
  user_id: string
  city: string
  country_code: string
  min_price: number | null
  max_price: number
  min_rooms: number | null
  max_rooms: number | null
  min_size_sqm: number | null
  max_size_sqm: number | null
  pet_friendly: boolean
  furnished: boolean | null
  keywords: string[] | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Listing {
  id: string
  source_site: string
  source_url: string
  title: string
  description: string | null
  price_eur_cents: number
  price_eur: number
  price_type: string
  rooms: number | null
  size_sqm: number | null
  city: string
  neighborhood: string | null
  country_code: string
  address: string | null
  pet_friendly: boolean | null
  furnished: boolean | null
  energy_label: string | null
  available_from: string | null
  rental_agent: string | null
  image_urls: string[]
  first_seen_at: string
}

export interface Match {
  id: string
  listing_id: string
  preference_id: string
  score: number
  notified: boolean
  notification_channel: string
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

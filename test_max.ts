import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);

async function main() {
  const { data, error } = await supabase
    .from("numbers4_daily_prediction_documents")
    .select("target_draw_number")
    .eq("doc_kind", "ensemble")
    .order("target_draw_number", { ascending: false })
    .limit(1);
    
  if (error) console.error(error);
  else console.log(data);
}
main().catch(console.error);

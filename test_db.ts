import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);

async function main() {
  const { data, error } = await supabase
    .from("numbers4_daily_prediction_documents")
    .select("doc_kind, method_slug, payload, relative_path")
    .eq("target_draw_number", 6955)
    .eq("doc_kind", "ensemble");
    
  if (error) console.error(error);
  else {
    const payload = data[0].payload;
    const preds = payload.predictions;
    const lastRun = preds[preds.length - 1];
    console.log(lastRun.next_model_predictions);
  }
}
main().catch(console.error);

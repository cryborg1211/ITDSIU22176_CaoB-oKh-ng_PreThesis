//+------------------------------------------------------------------+
//| ImportHoseSymbols.mq5                                             |
//| Creates one custom symbol per HOSE stock (<TICKER>.VN, group HOSE) |
//| from files written by scripts/export_mt5.py into                   |
//| Terminal/Common/Files/hose/.                                       |
//|                                                                    |
//| Each daily bar is stored as one M1 bar at 00:00, which is how MT5  |
//| keeps custom history; the D1 chart is built from it unchanged.     |
//| HOSE tick size depends on price (10 / 50 / 100 VND); a symbol has  |
//| one tick size, so it is set to the smallest and the EA rounds to   |
//| the real step.                                                     |
//+------------------------------------------------------------------+
#property copyright "Cao Bao Khuong - ITDSIU22176"
#property version   "1.00"
#property script_show_inputs

input string InpFolder     = "hose";  // folder under Common/Files
input string InpGroup      = "HOSE";  // custom symbol group
input string InpSuffix     = ".VN";   // avoids clashing with broker symbols
input int    InpMaxSymbols = 0;       // 0 = all symbols in symbols.csv
input bool   InpWatchOnly  = false;   // only the top-30 liquid names

//+------------------------------------------------------------------+
//| Each setter names the property it failed on, once per run.       |
//+------------------------------------------------------------------+
string g_reported = "";
void Report(const string name, const string prop)
  {
   int err = GetLastError();
   if(StringFind(g_reported, "|" + prop + "|") >= 0)
      return;
   g_reported += "|" + prop + "|";
   PrintFormat("%s: cannot set %s (error %d) -- further symbols not reported", name, prop, err);
  }
bool SetS(const string n, ENUM_SYMBOL_INFO_STRING p, const string v, const string label)
  {
   ResetLastError();
   if(CustomSymbolSetString(n, p, v)) return true;
   Report(n, label);
   return false;
  }
bool SetI(const string n, ENUM_SYMBOL_INFO_INTEGER p, const long v, const string label)
  {
   ResetLastError();
   if(CustomSymbolSetInteger(n, p, v)) return true;
   Report(n, label);
   return false;
  }
bool SetD(const string n, ENUM_SYMBOL_INFO_DOUBLE p, const double v, const string label)
  {
   ResetLastError();
   if(CustomSymbolSetDouble(n, p, v)) return true;
   Report(n, label);
   return false;
  }

//+------------------------------------------------------------------+
bool SetupSymbol(const string name, const string description)
  {
   if(!SymbolInfoInteger(name, SYMBOL_CUSTOM))
     {
      if(!CustomSymbolCreate(name, InpGroup, NULL))
        {
         PrintFormat("CustomSymbolCreate(%s) failed: %d", name, GetLastError());
         return false;
        }
     }
   // a failed property is reported and skipped: the bars are still imported
   SetS(name, SYMBOL_DESCRIPTION, description, "DESCRIPTION");
   SetS(name, SYMBOL_CURRENCY_BASE, "VND", "CURRENCY_BASE");
   SetS(name, SYMBOL_CURRENCY_PROFIT, "VND", "CURRENCY_PROFIT");
   SetS(name, SYMBOL_CURRENCY_MARGIN, "VND", "CURRENCY_MARGIN");
   SetI(name, SYMBOL_DIGITS, 0, "DIGITS");
   SetD(name, SYMBOL_POINT, 1.0, "POINT");
   SetD(name, SYMBOL_TRADE_TICK_SIZE, 10.0, "TRADE_TICK_SIZE");
   SetD(name, SYMBOL_TRADE_TICK_VALUE, 10.0, "TRADE_TICK_VALUE");
   SetD(name, SYMBOL_TRADE_CONTRACT_SIZE, 1.0, "TRADE_CONTRACT_SIZE");
   SetD(name, SYMBOL_VOLUME_MIN, 100.0, "VOLUME_MIN");
   SetD(name, SYMBOL_VOLUME_STEP, 100.0, "VOLUME_STEP");
   SetD(name, SYMBOL_VOLUME_MAX, 10000000.0, "VOLUME_MAX");
   SetI(name, SYMBOL_TRADE_CALC_MODE, SYMBOL_CALC_MODE_EXCH_STOCKS, "TRADE_CALC_MODE");
   SetI(name, SYMBOL_CHART_MODE, SYMBOL_CHART_MODE_LAST, "CHART_MODE");
   return true;
  }

//+------------------------------------------------------------------+
int LoadBars(const string ticker, MqlRates &rates[])
  {
   string path = InpFolder + "\\bars\\" + ticker + ".csv";
   int h = FileOpen(path, FILE_READ | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE)
     {
      PrintFormat("cannot open %s: %d", path, GetLastError());
      return 0;
     }
   for(int i = 0; i < 6; i++)
      FileReadString(h);                       // header
   int n = 0;
   ArrayResize(rates, 0, 2048);
   while(!FileIsEnding(h))
     {
      string d = FileReadString(h);
      if(d == "")
         break;
      MqlRates r;
      ZeroMemory(r);
      r.time        = StringToTime(d);
      r.open        = StringToDouble(FileReadString(h));
      r.high        = StringToDouble(FileReadString(h));
      r.low         = StringToDouble(FileReadString(h));
      r.close       = StringToDouble(FileReadString(h));
      r.tick_volume = (long)StringToInteger(FileReadString(h));
      r.real_volume = r.tick_volume;
      ArrayResize(rates, n + 1, 2048);
      rates[n++] = r;
     }
   FileClose(h);
   return n;
  }

//+------------------------------------------------------------------+
void OnStart()
  {
   string list = InpFolder + "\\symbols.csv";
   int h = FileOpen(list, FILE_READ | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE)
     {
      PrintFormat("cannot open %s: %d -- run scripts/export_mt5.py first", list, GetLastError());
      return;
     }
   for(int i = 0; i < 6; i++)
      FileReadString(h);                       // header
   int done = 0, failed = 0, selected = 0;
   long total_bars = 0;
   while(!FileIsEnding(h) && !IsStopped())
     {
      string ticker = FileReadString(h);
      if(ticker == "")
         break;
      string description = FileReadString(h);
      FileReadString(h);                       // first
      FileReadString(h);                       // last
      FileReadString(h);                       // bars
      bool watch = (StringToInteger(FileReadString(h)) == 1);
      if(InpWatchOnly && !watch)
         continue;
      if(InpMaxSymbols > 0 && done >= InpMaxSymbols)
         break;

      string name = ticker + InpSuffix;
      MqlRates rates[];
      int n = LoadBars(ticker, rates);
      if(n == 0 || !SetupSymbol(name, description))
        {
         failed++;
         continue;
        }
      int written = CustomRatesReplace(name, rates[0].time, rates[n - 1].time, rates);
      if(written != n)
        {
         PrintFormat("%s: wrote %d of %d bars (error %d)", name, written, n, GetLastError());
         failed++;
         continue;
        }
      if(watch && SymbolSelect(name, true))
         selected++;
      total_bars += n;
      done++;
     }
   FileClose(h);
   PrintFormat("HOSE import: %d symbols, %I64d bars, %d failed, %d added to Market Watch",
               done, total_bars, failed, selected);
  }
//+------------------------------------------------------------------+

/**
 * LoginShellWidgets — login page widget layout
 *
 *   Row 1: [ Login card (400px) ] [ Calendar (flex:2) ] [ Teacher Tip (flex:1) ]
 *   Row 2: [ News (flex:3) ]      [ Term Events (flex:3) ] [ Visitors (flex:2)  ]
 *
 * Data sources:
 *   Calendar : GET /api/calendar/events + GET /api/calendar/terms  (useCalendarData)
 *   News     : GET /api/news                                        (useNewsData)
 *   Visitors : localStorage counter seeded at 3 000
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, Pressable, ScrollView, StyleSheet,
  Platform, Animated, Easing,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useCalendarData } from './useCalendarData';
import { useNewsData } from './useNewsData';

// ─── palette ───────────────────────────────────────────────────────────────
const C = {
  primary:    '#5C6BC0',
  primaryDk:  '#3949AB',
  primaryBg:  '#EEF0FB',
  green:      '#16A34A',
  greenBg:    '#DCFCE7',
  teal:       '#0D9488',
  tealBg:     '#CCFBF1',
  amber:      '#D97706',
  amberBg:    '#FEF3C7',
  rose:       '#E11D48',
  roseBg:     '#FFE4E6',
  purple:     '#7C3AED',
  purpleBg:   '#EDE9FE',
  border:     '#E0E4F5',
  bg:         '#F0F2FF',
  card:       '#FFFFFF',
  title:      '#1E1B4B',
  sub:        '#4B5563',
  muted:      '#9CA3AF',
  red:        '#EF4444',
};

// Card base — applied as plain object (web boxShadow support)
const CARD: any = {
  backgroundColor: C.card,
  borderRadius: 16,
  borderWidth: 1,
  borderColor: C.border,
  boxShadow: '0 4px 20px rgba(92,107,192,0.09)',
};

// ─── helpers ───────────────────────────────────────────────────────────────
const MONTHS   = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];
const DAY_LBLS = ['S','M','T','W','T','F','S'];

function eventsForMonth(events: any[], year: number, month: number) {
  const out: {day:number;title:string;bg:string;tc:string;dot:string}[] = [];
  for (const ev of events) {
    if (!ev.isoDate) continue;
    const d = new Date(ev.isoDate);
    if (d.getFullYear()===year && d.getMonth()===month)
      out.push({day:d.getDate(),title:ev.title,bg:ev.bg,tc:ev.tc,dot:ev.dot});
  }
  return out;
}

const TAG_COLORS: Record<string,{bg:string;tc:string}> = {
  MoE:      {bg:'#EEF0FB',tc:'#4338CA'},
  KNEC:     {bg:'#FEF9C3',tc:'#854D0E'},
  KICD:     {bg:'#DCFCE7',tc:'#166534'},
  TSC:      {bg:'#FCE7F3',tc:'#9D174D'},
  Update:   {bg:'#F3F4F6',tc:'#374151'},
  UPDATE:   {bg:'#F3F4F6',tc:'#374151'},
  Tip:      {bg:'#FFF7ED',tc:'#C2410C'},
  Academic: {bg:'#EEF0FB',tc:'#4338CA'},
  Event:    {bg:'#DCFCE7',tc:'#166534'},
  Exam:     {bg:'#FEE2E2',tc:'#991B1B'},
};
const tagC = (tag:string) => TAG_COLORS[tag] ?? {bg:'#F3F4F6',tc:'#374151'};

// ─── TEACHER TIP CARD ─────────────────────────────────────────────────────
const TIPS = [
  { icon:'bulb',      color:C.amber,   bg:C.amberBg,   tip:'Start each lesson with a real-life scenario relevant to learners\' environment to boost engagement.' },
  { icon:'leaf',      color:C.green,   bg:C.greenBg,   tip:'Use differentiated tasks — a guided example, paired practice, then an independent challenge.' },
  { icon:'school',    color:C.primary, bg:C.primaryBg, tip:'Align your learning outcomes to KICD strand competencies before writing your lesson plan.' },
  { icon:'people',    color:C.teal,    bg:C.tealBg,    tip:'Group work boosts competency development — assign roles so every learner participates actively.' },
  { icon:'bar-chart', color:C.purple,  bg:C.purpleBg,  tip:'Formative assessment doesn\'t need to be formal — exit slips or a quick Q&A work just as well.' },
  { icon:'ribbon',    color:C.rose,    bg:C.roseBg,    tip:'Celebrate small wins in class — positive reinforcement improves learner confidence and attendance.' },
  { icon:'telescope', color:C.teal,    bg:C.tealBg,    tip:'CBC emphasises values, skills and competencies over rote memorization — plan accordingly.' },
  { icon:'pencil',    color:C.amber,   bg:C.amberBg,   tip:'Review your scheme of work weekly and align it with KICD guidelines to stay on track.' },
];

const TeacherTipCard: React.FC = () => {
  const [idx, setIdx] = useState(() => Math.floor(Math.random() * TIPS.length));
  const tip = TIPS[idx];
  const fadeAnim = useRef(new Animated.Value(1)).current;

  const next = () => {
    Animated.timing(fadeAnim,{toValue:0,duration:200,useNativeDriver:true}).start(()=>{
      setIdx(i=>(i+1)%TIPS.length);
      Animated.timing(fadeAnim,{toValue:1,duration:300,useNativeDriver:true}).start();
    });
  };
  const prev = () => {
    Animated.timing(fadeAnim,{toValue:0,duration:200,useNativeDriver:true}).start(()=>{
      setIdx(i=>(i-1+TIPS.length)%TIPS.length);
      Animated.timing(fadeAnim,{toValue:1,duration:300,useNativeDriver:true}).start();
    });
  };

  return (
    <View style={[CARD, tipS.card]}>
      {/* Coloured top bar */}
      <View style={[tipS.topBar, {backgroundColor: tip.color}]}/>

      {/* Header */}
      <View style={tipS.header}>
        <View style={[tipS.iconCircle, {backgroundColor: tip.bg}]}>
          <Ionicons name={tip.icon as any} size={22} color={tip.color}/>
        </View>
        <View style={{flex:1, marginLeft:12}}>
          <Text style={tipS.label}>Teacher's Tip</Text>
          <Text style={[tipS.counter, {color: tip.color}]}>{idx+1} of {TIPS.length}</Text>
        </View>
      </View>

      {/* Tip text */}
      <Animated.View style={[tipS.tipBox, {opacity: fadeAnim, backgroundColor: tip.bg}]}>
        <Text style={[tipS.quote, {color: tip.color}]}>"</Text>
        <Text style={tipS.tipText}>{tip.tip}</Text>
      </Animated.View>

      {/* Dots */}
      <View style={tipS.dots}>
        {TIPS.map((_,i)=>(
          <Pressable key={i} onPress={()=>setIdx(i)}>
            <View style={[tipS.dot, {backgroundColor: i===idx ? tip.color : C.border}]}/>
          </Pressable>
        ))}
      </View>

      {/* Nav */}
      <View style={tipS.nav}>
        <Pressable style={[tipS.navBtn, {borderColor: tip.color}]} onPress={prev}>
          <Ionicons name="chevron-back" size={14} color={tip.color}/>
          <Text style={[tipS.navTxt, {color: tip.color}]}>Prev</Text>
        </Pressable>
        <Pressable style={[tipS.navBtn, {backgroundColor: tip.color, borderColor: tip.color}]} onPress={next}>
          <Text style={[tipS.navTxt, {color:'#fff'}]}>Next</Text>
          <Ionicons name="chevron-forward" size={14} color="#fff"/>
        </Pressable>
      </View>
    </View>
  );
};

const tipS = StyleSheet.create({
  card:       { flex:1, overflow:'hidden', padding:0 },
  topBar:     { height:5, width:'100%', borderTopLeftRadius:16, borderTopRightRadius:16 },
  header:     { flexDirection:'row', alignItems:'center', padding:18, paddingBottom:12 },
  iconCircle: { width:44, height:44, borderRadius:22, alignItems:'center', justifyContent:'center' },
  label:      { fontSize:15, fontWeight:'700', color:C.title },
  counter:    { fontSize:12, fontWeight:'600', marginTop:2 },
  tipBox:     { marginHorizontal:18, borderRadius:12, padding:14, marginBottom:14 },
  quote:      { fontSize:36, fontWeight:'900', lineHeight:32, marginBottom:2 },
  tipText:    { fontSize:13, color:C.sub, lineHeight:20 },
  dots:       { flexDirection:'row', justifyContent:'center', gap:6, marginBottom:14 },
  dot:        { width:7, height:7, borderRadius:4 },
  nav:        { flexDirection:'row', gap:10, paddingHorizontal:18, paddingBottom:18 },
  navBtn:     { flex:1, flexDirection:'row', alignItems:'center', justifyContent:'center',
                gap:5, paddingVertical:9, borderRadius:10, borderWidth:1.5 },
  navTxt:     { fontSize:13, fontWeight:'600' },
});

// ─── VISITOR COUNTER ──────────────────────────────────────────────────────
const SEED = 3000; const LS_KEY = 'cbep_visit_count';
function getCount():number {
  if(typeof localStorage==='undefined') return SEED;
  try { const s=localStorage.getItem(LS_KEY); if(!s){const v=SEED+Math.floor(Math.random()*80);localStorage.setItem(LS_KEY,String(v));return v;} return parseInt(s,10)||SEED; } catch{return SEED;}
}
function incCount():number {
  if(typeof localStorage==='undefined') return SEED;
  try{const n=getCount()+1;localStorage.setItem(LS_KEY,String(n));return n;}catch{return SEED;}
}

function AnimatedCount({target}:{target:number}) {
  const anim=useRef(new Animated.Value(0)).current;
  const [val,setVal]=useState(0);
  useEffect(()=>{
    anim.setValue(0);
    Animated.timing(anim,{toValue:target,duration:1800,easing:Easing.out(Easing.cubic),useNativeDriver:false}).start();
    const id=anim.addListener(({value})=>setVal(Math.floor(value)));
    return()=>anim.removeListener(id);
  },[target]);
  return <Text style={vcS.bigNum}>{val.toLocaleString()}</Text>;
}

const VisitorCounterCard:React.FC=()=>{
  const [count,setCount]=useState(SEED);
  useEffect(()=>{setCount(incCount());},[]);
  const pct=Math.min((count/10000)*100,100);
  const R=52; const arc=Math.PI*R; const offset=arc-(pct/100)*arc;
  return (
    <View style={[CARD, vcS.card]}>
      <View style={[vcS.topBar]}/>
      <View style={vcS.header}>
        <View style={vcS.iconBox}><Ionicons name="people" size={20} color={C.teal}/></View>
        <View style={{flex:1,marginLeft:10}}>
          <Text style={vcS.title}>Website Visitors</Text>
          <Text style={vcS.sub}>All-time unique visits</Text>
        </View>
        <View style={vcS.liveBadge}>
          <View style={vcS.liveDot}/>
          <Text style={vcS.liveText}>LIVE</Text>
        </View>
      </View>
      <View style={vcS.gaugeWrap}>
        {Platform.OS==='web'?(
          // @ts-ignore
          <svg width="150" height="84" viewBox="0 0 150 84">
            {/* @ts-ignore */}<path d="M 11 78 A 64 64 0 0 1 139 78" fill="none" stroke="#E0F2FE" strokeWidth="13" strokeLinecap="round"/>
            {/* @ts-ignore */}<path d="M 11 78 A 64 64 0 0 1 139 78" fill="none" stroke={C.teal} strokeWidth="13" strokeLinecap="round"
              strokeDasharray={`${arc}`} strokeDashoffset={`${offset}`}
              style={{transition:'stroke-dashoffset 1.8s cubic-bezier(0.16,1,0.3,1)'}}/>
            {/* @ts-ignore */}<text x="75" y="72" textAnchor="middle" fontSize="13" fill={C.muted}>{pct.toFixed(1)}%</text>
          </svg>
        ):<View style={{height:84}}/>}
      </View>
      <AnimatedCount target={count}/>
      <Text style={vcS.label}>visitors since launch</Text>
      <View style={vcS.statRow}>
        <View style={vcS.statItem}>
          <Ionicons name="trending-up" size={14} color={C.green}/>
          <Text style={vcS.statVal}>+{Math.floor(count*0.03).toLocaleString()}</Text>
          <Text style={vcS.statLbl}>this month</Text>
        </View>
        <View style={vcS.div}/>
        <View style={vcS.statItem}>
          <Ionicons name="refresh" size={14} color={C.amber}/>
          <Text style={vcS.statVal}>{Math.floor(count*0.6).toLocaleString()}</Text>
          <Text style={vcS.statLbl}>returning</Text>
        </View>
      </View>
    </View>
  );
};

const vcS=StyleSheet.create({
  card:      {padding:0,flex:1,overflow:'hidden'},
  topBar:    {height:5,backgroundColor:C.teal},
  header:    {flexDirection:'row',alignItems:'center',padding:18,paddingBottom:10},
  iconBox:   {width:38,height:38,borderRadius:10,backgroundColor:C.tealBg,alignItems:'center',justifyContent:'center'},
  title:     {fontSize:15,fontWeight:'700',color:C.title},
  sub:       {fontSize:12,color:C.muted,marginTop:2},
  liveBadge: {flexDirection:'row',alignItems:'center',gap:5},
  liveDot:   {width:8,height:8,borderRadius:4,backgroundColor:'#22C55E'},
  liveText:  {fontSize:11,fontWeight:'700',color:C.green,letterSpacing:0.5},
  gaugeWrap: {alignItems:'center',marginBottom:2},
  bigNum:    {fontSize:38,fontWeight:'800',color:C.title,textAlign:'center',letterSpacing:-1},
  label:     {fontSize:13,color:C.muted,textAlign:'center',marginTop:2,marginBottom:14},
  statRow:   {flexDirection:'row',alignItems:'center',backgroundColor:C.tealBg,margin:16,marginTop:0,borderRadius:12,padding:12},
  statItem:  {flex:1,flexDirection:'row',alignItems:'center',gap:6,justifyContent:'center'},
  statVal:   {fontSize:14,fontWeight:'700',color:C.title},
  statLbl:   {fontSize:11,color:C.muted},
  div:       {width:1,height:28,backgroundColor:'#99F6E4'},
});

// ─── NEWS CARD ─────────────────────────────────────────────────────────────
const NewsCard:React.FC=()=>{
  const {items,loading}=useNewsData();
  return (
    <View style={[CARD, newsS.card]}>
      <View style={newsS.topBar}/>
      <View style={newsS.header}>
        <View style={newsS.iconBox}><Ionicons name="megaphone" size={18} color={C.purple}/></View>
        <View style={{flex:1,marginLeft:10}}>
          <Text style={newsS.title}>Latest Updates</Text>
          <Text style={newsS.sub}>Education news & announcements</Text>
        </View>
        <View style={newsS.badge}><Text style={newsS.badgeTxt}>LIVE</Text></View>
      </View>
      <View style={newsS.list}>
        {loading
          ?[0,1,2,3].map(i=>(
              <View key={i} style={newsS.skelRow}>
                <View style={newsS.skelTag}/><View style={newsS.skelLine}/>
              </View>
            ))
          :items.slice(0,6).map((item,i)=>{
              const tc=tagC(item.tag);
              return (
                <View key={i} style={[newsS.row, i<5&&newsS.rowBorder]}>
                  <View style={[newsS.tag,{backgroundColor:tc.bg}]}>
                    <Text style={[newsS.tagTxt,{color:tc.tc}]}>{item.tag}</Text>
                  </View>
                  <Text style={newsS.text} numberOfLines={2}>{item.text}</Text>
                </View>
              );
            })}
      </View>
    </View>
  );
};

const newsS=StyleSheet.create({
  card:     {flex:1,overflow:'hidden',padding:0},
  topBar:   {height:5,backgroundColor:C.purple},
  header:   {flexDirection:'row',alignItems:'center',padding:18,paddingBottom:12},
  iconBox:  {width:38,height:38,borderRadius:10,backgroundColor:C.purpleBg,alignItems:'center',justifyContent:'center'},
  title:    {fontSize:15,fontWeight:'700',color:C.title},
  sub:      {fontSize:12,color:C.muted,marginTop:2},
  badge:    {backgroundColor:C.greenBg,paddingHorizontal:9,paddingVertical:3,borderRadius:20},
  badgeTxt: {fontSize:10,fontWeight:'700',color:C.green,letterSpacing:0.5},
  list:     {paddingHorizontal:18,paddingBottom:14},
  row:      {flexDirection:'row',alignItems:'flex-start',gap:10,paddingVertical:10},
  rowBorder:{borderBottomWidth:1,borderBottomColor:C.border},
  tag:      {paddingHorizontal:8,paddingVertical:3,borderRadius:6,flexShrink:0,marginTop:2},
  tagTxt:   {fontSize:10,fontWeight:'700'},
  text:     {flex:1,fontSize:13,color:C.sub,lineHeight:19},
  skelRow:  {flexDirection:'row',alignItems:'center',gap:10,paddingVertical:10},
  skelTag:  {width:40,height:20,borderRadius:6,backgroundColor:C.border},
  skelLine: {flex:1,height:15,borderRadius:6,backgroundColor:C.border},
});

// ─── MONTHLY CALENDAR ──────────────────────────────────────────────────────
const MonthlyCalendarCard:React.FC=()=>{
  const {events}=useCalendarData();
  const today=new Date();
  const [month,setMonth]=useState(today.getMonth());
  const [year,setYear]=useState(today.getFullYear());
  const [openDay,setOpenDay]=useState<number|null>(null);

  const monthEvs=eventsForMonth(events,year,month);
  const byDay=new Map<number,typeof monthEvs>();
  for(const e of monthEvs){const l=byDay.get(e.day)??[];l.push(e);byDay.set(e.day,l);}

  const firstDow=new Date(year,month,1).getDay();
  const daysInMonth=new Date(year,month+1,0).getDate();
  const isCurMonth=month===today.getMonth()&&year===today.getFullYear();

  const cells:(number|null)[]=[];
  for(let i=0;i<firstDow;i++)cells.push(null);
  for(let d=1;d<=daysInMonth;d++)cells.push(d);
  while(cells.length%7!==0)cells.push(null);

  const goPrev=()=>{setOpenDay(null);month===0?(setMonth(11),setYear(y=>y-1)):setMonth(m=>m-1);};
  const goNext=()=>{setOpenDay(null);month===11?(setMonth(0),setYear(y=>y+1)):setMonth(m=>m+1);};

  return (
    <View style={[CARD, calS.card]}>
      <View style={calS.topBar}/>
      {/* Header */}
      <View style={calS.header}>
        <View style={calS.titleRow}>
          <Ionicons name="calendar" size={17} color={C.primary} style={{marginRight:8}}/>
          <Text style={calS.title}>Academic Calendar</Text>
        </View>
        <View style={calS.navRow}>
          <Pressable onPress={goPrev} style={calS.navBtn} hitSlop={8}>
            <Ionicons name="chevron-back" size={14} color={C.primary}/>
          </Pressable>
          <Text style={calS.monthLbl}>{MONTHS[month]} {year}</Text>
          <Pressable onPress={goNext} style={calS.navBtn} hitSlop={8}>
            <Ionicons name="chevron-forward" size={14} color={C.primary}/>
          </Pressable>
        </View>
      </View>

      {/* Day headers */}
      <View style={calS.row}>
        {DAY_LBLS.map((l,i)=>(
          <View key={i} style={calS.cell}>
            <Text style={calS.dayLbl}>{l}</Text>
          </View>
        ))}
      </View>

      {/* Grid */}
      <View style={{flex:1,justifyContent:'space-evenly',paddingHorizontal:6,paddingBottom:4}}>
        {Array.from({length:cells.length/7}).map((_,row)=>(
          <View key={row} style={calS.row}>
            {cells.slice(row*7,row*7+7).map((day,col)=>{
              if(day===null) return <View key={col} style={calS.cell}/>;
              const evs=byDay.get(day);
              const isToday=isCurMonth&&day===today.getDate();
              const first=evs?.[0];
              return (
                <Pressable key={col} style={calS.cell}
                  onPress={()=>evs&&setOpenDay(c=>c===day?null:day)}>
                  <View style={[
                    calS.pill,
                    isToday&&calS.pillToday,
                    evs&&first&&!isToday&&{backgroundColor:first.bg},
                  ]}>
                    <Text style={[
                      calS.dayNum,
                      isToday&&calS.dayNumToday,
                      evs&&first&&!isToday&&{color:first.tc,fontWeight:'700'},
                    ]}>{day}</Text>
                    {evs&&first&&!isToday&&(
                      <View style={[calS.dot,{backgroundColor:first.dot}]}/>
                    )}
                  </View>
                </Pressable>
              );
            })}
          </View>
        ))}
      </View>

      {/* Popover */}
      {openDay!==null&&byDay.has(openDay)&&(
        <View style={calS.popover}>
          <View style={calS.popHead}>
            <Text style={calS.popDate}>{MONTHS[month]} {openDay}</Text>
            <Pressable onPress={()=>setOpenDay(null)} hitSlop={8}>
              <Ionicons name="close" size={14} color={C.sub}/>
            </Pressable>
          </View>
          {(byDay.get(openDay)??[]).map((e,i)=>(
            <View key={i} style={calS.popRow}>
              <View style={[calS.popDot,{backgroundColor:e.dot}]}/>
              <Text style={calS.popTitle}>{e.title}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Legend */}
      <View style={calS.legend}>
        {[{color:C.primary,label:'Academic'},{color:C.green,label:'Co-curr'},{color:C.red,label:'Exams'}].map(({color,label})=>(
          <View key={label} style={calS.legendItem}>
            <View style={[calS.legendDot,{backgroundColor:color}]}/>
            <Text style={calS.legendLbl}>{label}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const calS=StyleSheet.create({
  card:       {flex:1,overflow:'hidden',padding:0},
  topBar:     {height:5,backgroundColor:C.primary},
  header:     {flexDirection:'row',justifyContent:'space-between',alignItems:'center',paddingHorizontal:16,paddingTop:14,paddingBottom:8},
  titleRow:   {flexDirection:'row',alignItems:'center'},
  title:      {fontSize:15,fontWeight:'700',color:C.title},
  navRow:     {flexDirection:'row',alignItems:'center',gap:8},
  navBtn:     {width:28,height:28,borderRadius:8,backgroundColor:C.primaryBg,alignItems:'center',justifyContent:'center'},
  monthLbl:   {fontSize:14,fontWeight:'600',color:C.primary,minWidth:110,textAlign:'center'},
  row:        {flexDirection:'row'},
  cell:       {flex:1,alignItems:'center',paddingVertical:3},
  dayLbl:     {fontSize:12,fontWeight:'600',color:C.muted,textTransform:'uppercase'},
  pill:       {width:32,height:32,borderRadius:9,alignItems:'center',justifyContent:'center'},
  pillToday:  {backgroundColor:C.primary},
  dot:        {width:4,height:4,borderRadius:2,marginTop:1},
  dayNum:     {fontSize:13,color:C.title},
  dayNumToday:{color:'#FFFFFF',fontWeight:'700'},
  popover:    {
    position:'absolute',bottom:46,left:14,right:14,
    backgroundColor:'#FFFFFF',borderRadius:10,padding:14,
    borderWidth:1,borderColor:C.border,
    // @ts-ignore
    boxShadow:'0 8px 24px rgba(92,107,192,0.18)',zIndex:10,
  },
  popHead:    {flexDirection:'row',justifyContent:'space-between',marginBottom:8},
  popDate:    {fontSize:13,fontWeight:'700',color:C.title},
  popRow:     {flexDirection:'row',alignItems:'center',gap:8,marginTop:5},
  popDot:     {width:7,height:7,borderRadius:4},
  popTitle:   {fontSize:13,color:C.sub,flex:1},
  legend:     {flexDirection:'row',gap:14,paddingVertical:10,justifyContent:'center',borderTopWidth:1,borderTopColor:C.border,marginHorizontal:16},
  legendItem: {flexDirection:'row',alignItems:'center',gap:5},
  legendDot:  {width:8,height:8,borderRadius:4},
  legendLbl:  {fontSize:12,color:C.muted},
});

// ─── TERM EVENTS CARD ──────────────────────────────────────────────────────
const TermEventsCard:React.FC=()=>{
  const {terms,loading}=useCalendarData();
  const titleYear=terms[0]?.year||new Date().getFullYear();
  const visible=(terms.filter(t=>t.status!=='past').length>0
    ?terms.filter(t=>t.status!=='past'):terms).slice(0,2);
  return (
    <View style={[CARD, termS.card]}>
      <View style={termS.topBar}/>
      <View style={termS.header}>
        <View style={termS.iconBox}>
          <Ionicons name="calendar-number" size={18} color={C.green}/>
        </View>
        <View style={{marginLeft:10}}>
          <Text style={termS.title}>{titleYear} Term Calendar</Text>
          <Text style={termS.sub}>Academic & co-curricular activities</Text>
        </View>
      </View>
      {loading
        ?<Text style={termS.empty}>Loading…</Text>
        :visible.length===0
          ?<Text style={termS.empty}>No term data available.</Text>
          :(
            <View style={termS.grid}>
              {visible.map(term=>(
                <View key={term.id} style={termS.col}>
                  <View style={[termS.badge,{backgroundColor:term.headerBg}]}>
                    <Text style={[termS.termName,{color:term.headerText}]}>{term.name}</Text>
                    <Text style={termS.period}>{term.period}</Text>
                    <View style={[termS.pill,{
                      backgroundColor:term.status==='current'?'#DCFCE7':term.status==='past'?'#F3F4F6':'#EEF0FB',
                    }]}>
                      <Text style={[termS.pillTxt,{
                        color:term.status==='current'?C.green:term.status==='past'?C.muted:C.primary,
                      }]}>{term.displayStatus}</Text>
                    </View>
                  </View>
                  <View style={termS.section}>
                    <Text style={termS.sectionLbl}>📚 ACADEMIC</Text>
                    {term.academic.slice(0,3).map((a,i)=>(
                      <View key={i} style={termS.evRow}>
                        <View style={[termS.dot,{backgroundColor:C.primary}]}/>
                        <Text style={termS.evLbl} numberOfLines={1}>{a.label}</Text>
                        <Text style={termS.evDate}>{a.date}</Text>
                      </View>
                    ))}
                  </View>
                  <View style={termS.section}>
                    <Text style={[termS.sectionLbl,{color:C.green}]}>🏆 CO-CURR</Text>
                    {term.cocurricular.slice(0,3).map((a,i)=>(
                      <View key={i} style={termS.evRow}>
                        <View style={[termS.dot,{backgroundColor:C.green}]}/>
                        <Text style={termS.evLbl} numberOfLines={1}>{a.label}</Text>
                        <Text style={termS.evDate}>{a.date}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              ))}
            </View>
          )}
    </View>
  );
};

const termS=StyleSheet.create({
  card:       {flex:1,overflow:'hidden',padding:0},
  topBar:     {height:5,backgroundColor:C.green},
  header:     {flexDirection:'row',alignItems:'center',padding:18,paddingBottom:12},
  iconBox:    {width:38,height:38,borderRadius:10,backgroundColor:C.greenBg,alignItems:'center',justifyContent:'center'},
  title:      {fontSize:15,fontWeight:'700',color:C.title},
  sub:        {fontSize:12,color:C.muted,marginTop:2},
  empty:      {fontSize:13,color:C.muted,textAlign:'center',padding:20},
  grid:       {flexDirection:'row',gap:12,paddingHorizontal:18,paddingBottom:18},
  col:        {flex:1},
  badge:      {borderRadius:10,padding:12,marginBottom:10},
  termName:   {fontSize:14,fontWeight:'700'},
  period:     {fontSize:11,color:C.sub,marginTop:2},
  pill:       {marginTop:7,alignSelf:'flex-start',paddingHorizontal:9,paddingVertical:3,borderRadius:20},
  pillTxt:    {fontSize:11,fontWeight:'700'},
  section:    {marginBottom:10},
  sectionLbl: {fontSize:10,fontWeight:'700',color:C.primary,letterSpacing:0.5,marginBottom:6},
  evRow:      {flexDirection:'row',alignItems:'center',gap:7,paddingVertical:4},
  dot:        {width:6,height:6,borderRadius:3,flexShrink:0},
  evLbl:      {flex:1,fontSize:13,color:C.sub},
  evDate:     {fontSize:11,color:C.muted,flexShrink:0},
});

// ─── ROOT LAYOUT ───────────────────────────────────────────────────────────
interface Props { loginCard: React.ReactNode; }

export const LoginShellWidgets: React.FC<Props> = ({ loginCard }) => (
  <ScrollView
    style={shell.scroll}
    contentContainerStyle={shell.content}
    keyboardShouldPersistTaps="handled"
    showsVerticalScrollIndicator={false}
  >
    {/* Row 1 — Login card | Calendar | Teacher Tip (all same height) */}
    <View style={shell.row}>
      <View style={[CARD, shell.loginWrap]}>{loginCard}</View>
      <View style={shell.calWrap}><MonthlyCalendarCard /></View>
      <View style={shell.tipWrap}><TeacherTipCard /></View>
    </View>

    {/* Row 2 — News | Term Events | Visitor Counter */}
    <View style={shell.row}>
      <View style={shell.newsWrap}><NewsCard /></View>
      <View style={shell.termWrap}><TermEventsCard /></View>
      <View style={shell.gaugeWrap}><VisitorCounterCard /></View>
    </View>
  </ScrollView>
);

const shell=StyleSheet.create({
  scroll:    {flex:1,backgroundColor:'transparent'},
  content:   {padding:20,gap:16,flexGrow:1},
  row:       {flexDirection:'row',gap:16,alignItems:'stretch'},
  loginWrap: {width:380,flexShrink:0,padding:28},
  calWrap:   {flex:2},
  tipWrap:   {flex:1},
  newsWrap:  {flex:3},
  termWrap:  {flex:3},
  gaugeWrap: {flex:2},
});

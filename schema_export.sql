--
-- PostgreSQL database dump
--

\restrict 9wCs4PcioSDiUGYBc15k8OJZDKnXQQZ0sfmd4bFWxKAZK8I8r7FYMl9kZBu89U6

-- Dumped from database version 14.19 (Debian 14.19-1.pgdg13+1)
-- Dumped by pg_dump version 14.19 (Debian 14.19-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: LotteryType; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public."LotteryType" AS ENUM (
    'NUMBERS3',
    'NUMBERS4',
    'LOTO6'
);


ALTER TYPE public."LotteryType" OWNER TO "user";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: _prisma_migrations; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public._prisma_migrations (
    id character varying(36) NOT NULL,
    checksum character varying(64) NOT NULL,
    finished_at timestamp with time zone,
    migration_name character varying(255) NOT NULL,
    logs text,
    rolled_back_at timestamp with time zone,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    applied_steps_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public._prisma_migrations OWNER TO "user";

--
-- Name: comments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.comments (
    id text NOT NULL,
    "userId" text NOT NULL,
    "predictionId" text NOT NULL,
    content text NOT NULL,
    "isHidden" boolean DEFAULT false NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


ALTER TABLE public.comments OWNER TO "user";

--
-- Name: likes; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.likes (
    id text NOT NULL,
    "userId" text NOT NULL,
    "predictionId" text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.likes OWNER TO "user";

--
-- Name: loto6_draws; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.loto6_draws (
    draw_number integer NOT NULL,
    draw_date text NOT NULL,
    numbers text NOT NULL,
    bonus_number integer NOT NULL
);


ALTER TABLE public.loto6_draws OWNER TO "user";

--
-- Name: loto6_ensemble_predictions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.loto6_ensemble_predictions (
    id integer NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    target_draw_number integer,
    model_updated_at text,
    model_events_count integer,
    ensemble_weights text NOT NULL,
    predictions_count integer NOT NULL,
    top_predictions text NOT NULL,
    model_predictions text NOT NULL,
    actual_draw_number integer,
    actual_numbers text,
    actual_bonus_number integer,
    hit_status text,
    hit_count integer,
    bonus_hit boolean,
    notes text
);


ALTER TABLE public.loto6_ensemble_predictions OWNER TO "user";

--
-- Name: loto6_ensemble_predictions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.loto6_ensemble_predictions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.loto6_ensemble_predictions_id_seq OWNER TO "user";

--
-- Name: loto6_ensemble_predictions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.loto6_ensemble_predictions_id_seq OWNED BY public.loto6_ensemble_predictions.id;


--
-- Name: loto6_model_events; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.loto6_model_events (
    id integer NOT NULL,
    event_ts text NOT NULL,
    actual_number text NOT NULL,
    predictions text NOT NULL,
    hit_exact integer DEFAULT 0 NOT NULL,
    top_match text,
    max_position_hits integer NOT NULL,
    notes text
);


ALTER TABLE public.loto6_model_events OWNER TO "user";

--
-- Name: loto6_model_events_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.loto6_model_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.loto6_model_events_id_seq OWNER TO "user";

--
-- Name: loto6_model_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.loto6_model_events_id_seq OWNED BY public.loto6_model_events.id;


--
-- Name: loto6_prediction_candidates; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.loto6_prediction_candidates (
    id integer NOT NULL,
    ensemble_prediction_id integer NOT NULL,
    rank integer NOT NULL,
    number text NOT NULL,
    score double precision NOT NULL,
    contributing_models text NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.loto6_prediction_candidates OWNER TO "user";

--
-- Name: loto6_prediction_candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.loto6_prediction_candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.loto6_prediction_candidates_id_seq OWNER TO "user";

--
-- Name: loto6_prediction_candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.loto6_prediction_candidates_id_seq OWNED BY public.loto6_prediction_candidates.id;


--
-- Name: loto6_predictions_log; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.loto6_predictions_log (
    id integer NOT NULL,
    created_at text NOT NULL,
    source text NOT NULL,
    label text,
    number text NOT NULL,
    target_draw_number integer
);


ALTER TABLE public.loto6_predictions_log OWNER TO "user";

--
-- Name: loto6_predictions_log_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.loto6_predictions_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.loto6_predictions_log_id_seq OWNER TO "user";

--
-- Name: loto6_predictions_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.loto6_predictions_log_id_seq OWNED BY public.loto6_predictions_log.id;


--
-- Name: numbers3_draws; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers3_draws (
    draw_number integer NOT NULL,
    draw_date text NOT NULL,
    numbers text NOT NULL
);


ALTER TABLE public.numbers3_draws OWNER TO "user";

--
-- Name: numbers3_ensemble_predictions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers3_ensemble_predictions (
    id integer NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    target_draw_number integer,
    model_updated_at text,
    model_events_count integer,
    ensemble_weights text NOT NULL,
    predictions_count integer NOT NULL,
    top_predictions text NOT NULL,
    model_predictions text NOT NULL,
    actual_draw_number integer,
    actual_numbers text,
    hit_status text,
    hit_count integer,
    notes text
);


ALTER TABLE public.numbers3_ensemble_predictions OWNER TO "user";

--
-- Name: numbers3_ensemble_predictions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers3_ensemble_predictions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers3_ensemble_predictions_id_seq OWNER TO "user";

--
-- Name: numbers3_ensemble_predictions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers3_ensemble_predictions_id_seq OWNED BY public.numbers3_ensemble_predictions.id;


--
-- Name: numbers3_model_events; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers3_model_events (
    id integer NOT NULL,
    event_ts text NOT NULL,
    actual_number text NOT NULL,
    predictions text NOT NULL,
    hit_exact integer DEFAULT 0 NOT NULL,
    top_match text,
    max_position_hits integer NOT NULL,
    notes text
);


ALTER TABLE public.numbers3_model_events OWNER TO "user";

--
-- Name: numbers3_model_events_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers3_model_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers3_model_events_id_seq OWNER TO "user";

--
-- Name: numbers3_model_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers3_model_events_id_seq OWNED BY public.numbers3_model_events.id;


--
-- Name: numbers3_prediction_candidates; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers3_prediction_candidates (
    id integer NOT NULL,
    ensemble_prediction_id integer NOT NULL,
    rank integer NOT NULL,
    number text NOT NULL,
    score double precision NOT NULL,
    contributing_models text NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.numbers3_prediction_candidates OWNER TO "user";

--
-- Name: numbers3_prediction_candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers3_prediction_candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers3_prediction_candidates_id_seq OWNER TO "user";

--
-- Name: numbers3_prediction_candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers3_prediction_candidates_id_seq OWNED BY public.numbers3_prediction_candidates.id;


--
-- Name: numbers3_predictions_log; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers3_predictions_log (
    id integer NOT NULL,
    created_at text NOT NULL,
    source text NOT NULL,
    label text,
    number text NOT NULL,
    target_draw_number integer
);


ALTER TABLE public.numbers3_predictions_log OWNER TO "user";

--
-- Name: numbers3_predictions_log_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers3_predictions_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers3_predictions_log_id_seq OWNER TO "user";

--
-- Name: numbers3_predictions_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers3_predictions_log_id_seq OWNED BY public.numbers3_predictions_log.id;


--
-- Name: numbers4_draws; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers4_draws (
    draw_number integer NOT NULL,
    draw_date text NOT NULL,
    numbers text NOT NULL
);


ALTER TABLE public.numbers4_draws OWNER TO "user";

--
-- Name: numbers4_ensemble_predictions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers4_ensemble_predictions (
    id integer NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    target_draw_number integer,
    model_updated_at text,
    model_events_count integer,
    ensemble_weights text NOT NULL,
    predictions_count integer NOT NULL,
    top_predictions text NOT NULL,
    model_predictions text NOT NULL,
    actual_draw_number integer,
    actual_numbers text,
    hit_status text,
    hit_count integer,
    notes text
);


ALTER TABLE public.numbers4_ensemble_predictions OWNER TO "user";

--
-- Name: numbers4_ensemble_predictions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers4_ensemble_predictions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers4_ensemble_predictions_id_seq OWNER TO "user";

--
-- Name: numbers4_ensemble_predictions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers4_ensemble_predictions_id_seq OWNED BY public.numbers4_ensemble_predictions.id;


--
-- Name: numbers4_model_events; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers4_model_events (
    id integer NOT NULL,
    event_ts text NOT NULL,
    actual_number text NOT NULL,
    predictions text NOT NULL,
    hit_exact integer DEFAULT 0 NOT NULL,
    top_match text,
    max_position_hits integer NOT NULL,
    notes text
);


ALTER TABLE public.numbers4_model_events OWNER TO "user";

--
-- Name: numbers4_model_events_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers4_model_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers4_model_events_id_seq OWNER TO "user";

--
-- Name: numbers4_model_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers4_model_events_id_seq OWNED BY public.numbers4_model_events.id;


--
-- Name: numbers4_prediction_candidates; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers4_prediction_candidates (
    id integer NOT NULL,
    ensemble_prediction_id integer NOT NULL,
    rank integer NOT NULL,
    number text NOT NULL,
    score double precision NOT NULL,
    contributing_models text NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.numbers4_prediction_candidates OWNER TO "user";

--
-- Name: numbers4_prediction_candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers4_prediction_candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers4_prediction_candidates_id_seq OWNER TO "user";

--
-- Name: numbers4_prediction_candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers4_prediction_candidates_id_seq OWNED BY public.numbers4_prediction_candidates.id;


--
-- Name: numbers4_predictions_log; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.numbers4_predictions_log (
    id integer NOT NULL,
    created_at text NOT NULL,
    source text NOT NULL,
    label text,
    number text NOT NULL,
    target_draw_number integer
);


ALTER TABLE public.numbers4_predictions_log OWNER TO "user";

--
-- Name: numbers4_predictions_log_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.numbers4_predictions_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.numbers4_predictions_log_id_seq OWNER TO "user";

--
-- Name: numbers4_predictions_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.numbers4_predictions_log_id_seq OWNED BY public.numbers4_predictions_log.id;


--
-- Name: predictions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.predictions (
    id text NOT NULL,
    "userId" text NOT NULL,
    "lotteryType" public."LotteryType" NOT NULL,
    numbers text NOT NULL,
    "bonusNumber" integer,
    confidence double precision,
    reasoning text,
    "targetDrawNumber" integer,
    "targetDrawDate" timestamp(3) without time zone,
    "isPublic" boolean DEFAULT true NOT NULL,
    "isHidden" boolean DEFAULT false NOT NULL,
    "flagCount" integer DEFAULT 0 NOT NULL,
    "actualDrawNumber" integer,
    "actualNumbers" text,
    "actualBonusNumber" integer,
    "hitStatus" text,
    "hitCount" integer,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


ALTER TABLE public.predictions OWNER TO "user";

--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.users (
    id text NOT NULL,
    email text NOT NULL,
    username text,
    "displayName" text,
    "avatarUrl" text,
    bio text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO "user";

--
-- Name: loto6_ensemble_predictions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_ensemble_predictions ALTER COLUMN id SET DEFAULT nextval('public.loto6_ensemble_predictions_id_seq'::regclass);


--
-- Name: loto6_model_events id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_model_events ALTER COLUMN id SET DEFAULT nextval('public.loto6_model_events_id_seq'::regclass);


--
-- Name: loto6_prediction_candidates id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_prediction_candidates ALTER COLUMN id SET DEFAULT nextval('public.loto6_prediction_candidates_id_seq'::regclass);


--
-- Name: loto6_predictions_log id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_predictions_log ALTER COLUMN id SET DEFAULT nextval('public.loto6_predictions_log_id_seq'::regclass);


--
-- Name: numbers3_ensemble_predictions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_ensemble_predictions ALTER COLUMN id SET DEFAULT nextval('public.numbers3_ensemble_predictions_id_seq'::regclass);


--
-- Name: numbers3_model_events id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_model_events ALTER COLUMN id SET DEFAULT nextval('public.numbers3_model_events_id_seq'::regclass);


--
-- Name: numbers3_prediction_candidates id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_prediction_candidates ALTER COLUMN id SET DEFAULT nextval('public.numbers3_prediction_candidates_id_seq'::regclass);


--
-- Name: numbers3_predictions_log id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_predictions_log ALTER COLUMN id SET DEFAULT nextval('public.numbers3_predictions_log_id_seq'::regclass);


--
-- Name: numbers4_ensemble_predictions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_ensemble_predictions ALTER COLUMN id SET DEFAULT nextval('public.numbers4_ensemble_predictions_id_seq'::regclass);


--
-- Name: numbers4_model_events id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_model_events ALTER COLUMN id SET DEFAULT nextval('public.numbers4_model_events_id_seq'::regclass);


--
-- Name: numbers4_prediction_candidates id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_prediction_candidates ALTER COLUMN id SET DEFAULT nextval('public.numbers4_prediction_candidates_id_seq'::regclass);


--
-- Name: numbers4_predictions_log id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_predictions_log ALTER COLUMN id SET DEFAULT nextval('public.numbers4_predictions_log_id_seq'::regclass);


--
-- Name: _prisma_migrations _prisma_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public._prisma_migrations
    ADD CONSTRAINT _prisma_migrations_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: likes likes_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_pkey PRIMARY KEY (id);


--
-- Name: loto6_draws loto6_draws_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_draws
    ADD CONSTRAINT loto6_draws_pkey PRIMARY KEY (draw_number);


--
-- Name: loto6_ensemble_predictions loto6_ensemble_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_ensemble_predictions
    ADD CONSTRAINT loto6_ensemble_predictions_pkey PRIMARY KEY (id);


--
-- Name: loto6_model_events loto6_model_events_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_model_events
    ADD CONSTRAINT loto6_model_events_pkey PRIMARY KEY (id);


--
-- Name: loto6_prediction_candidates loto6_prediction_candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_prediction_candidates
    ADD CONSTRAINT loto6_prediction_candidates_pkey PRIMARY KEY (id);


--
-- Name: loto6_predictions_log loto6_predictions_log_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.loto6_predictions_log
    ADD CONSTRAINT loto6_predictions_log_pkey PRIMARY KEY (id);


--
-- Name: numbers3_draws numbers3_draws_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_draws
    ADD CONSTRAINT numbers3_draws_pkey PRIMARY KEY (draw_number);


--
-- Name: numbers3_ensemble_predictions numbers3_ensemble_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_ensemble_predictions
    ADD CONSTRAINT numbers3_ensemble_predictions_pkey PRIMARY KEY (id);


--
-- Name: numbers3_model_events numbers3_model_events_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_model_events
    ADD CONSTRAINT numbers3_model_events_pkey PRIMARY KEY (id);


--
-- Name: numbers3_prediction_candidates numbers3_prediction_candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_prediction_candidates
    ADD CONSTRAINT numbers3_prediction_candidates_pkey PRIMARY KEY (id);


--
-- Name: numbers3_predictions_log numbers3_predictions_log_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers3_predictions_log
    ADD CONSTRAINT numbers3_predictions_log_pkey PRIMARY KEY (id);


--
-- Name: numbers4_draws numbers4_draws_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_draws
    ADD CONSTRAINT numbers4_draws_pkey PRIMARY KEY (draw_number);


--
-- Name: numbers4_ensemble_predictions numbers4_ensemble_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_ensemble_predictions
    ADD CONSTRAINT numbers4_ensemble_predictions_pkey PRIMARY KEY (id);


--
-- Name: numbers4_model_events numbers4_model_events_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_model_events
    ADD CONSTRAINT numbers4_model_events_pkey PRIMARY KEY (id);


--
-- Name: numbers4_prediction_candidates numbers4_prediction_candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_prediction_candidates
    ADD CONSTRAINT numbers4_prediction_candidates_pkey PRIMARY KEY (id);


--
-- Name: numbers4_predictions_log numbers4_predictions_log_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.numbers4_predictions_log
    ADD CONSTRAINT numbers4_predictions_log_pkey PRIMARY KEY (id);


--
-- Name: predictions predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: comments_createdAt_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "comments_createdAt_idx" ON public.comments USING btree ("createdAt");


--
-- Name: comments_predictionId_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "comments_predictionId_idx" ON public.comments USING btree ("predictionId");


--
-- Name: comments_userId_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "comments_userId_idx" ON public.comments USING btree ("userId");


--
-- Name: likes_predictionId_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "likes_predictionId_idx" ON public.likes USING btree ("predictionId");


--
-- Name: likes_userId_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "likes_userId_idx" ON public.likes USING btree ("userId");


--
-- Name: likes_userId_predictionId_key; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX "likes_userId_predictionId_key" ON public.likes USING btree ("userId", "predictionId");


--
-- Name: loto6_ensemble_predictions_created_at_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX loto6_ensemble_predictions_created_at_idx ON public.loto6_ensemble_predictions USING btree (created_at);


--
-- Name: loto6_ensemble_predictions_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX loto6_ensemble_predictions_target_draw_number_idx ON public.loto6_ensemble_predictions USING btree (target_draw_number);


--
-- Name: loto6_prediction_candidates_ensemble_prediction_id_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX loto6_prediction_candidates_ensemble_prediction_id_idx ON public.loto6_prediction_candidates USING btree (ensemble_prediction_id);


--
-- Name: loto6_prediction_candidates_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX loto6_prediction_candidates_number_idx ON public.loto6_prediction_candidates USING btree (number);


--
-- Name: loto6_predictions_log_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX loto6_predictions_log_target_draw_number_idx ON public.loto6_predictions_log USING btree (target_draw_number);


--
-- Name: numbers3_ensemble_predictions_created_at_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers3_ensemble_predictions_created_at_idx ON public.numbers3_ensemble_predictions USING btree (created_at);


--
-- Name: numbers3_ensemble_predictions_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers3_ensemble_predictions_target_draw_number_idx ON public.numbers3_ensemble_predictions USING btree (target_draw_number);


--
-- Name: numbers3_prediction_candidates_ensemble_prediction_id_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers3_prediction_candidates_ensemble_prediction_id_idx ON public.numbers3_prediction_candidates USING btree (ensemble_prediction_id);


--
-- Name: numbers3_prediction_candidates_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers3_prediction_candidates_number_idx ON public.numbers3_prediction_candidates USING btree (number);


--
-- Name: numbers3_predictions_log_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers3_predictions_log_target_draw_number_idx ON public.numbers3_predictions_log USING btree (target_draw_number);


--
-- Name: numbers4_ensemble_predictions_created_at_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers4_ensemble_predictions_created_at_idx ON public.numbers4_ensemble_predictions USING btree (created_at);


--
-- Name: numbers4_ensemble_predictions_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers4_ensemble_predictions_target_draw_number_idx ON public.numbers4_ensemble_predictions USING btree (target_draw_number);


--
-- Name: numbers4_prediction_candidates_ensemble_prediction_id_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers4_prediction_candidates_ensemble_prediction_id_idx ON public.numbers4_prediction_candidates USING btree (ensemble_prediction_id);


--
-- Name: numbers4_prediction_candidates_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers4_prediction_candidates_number_idx ON public.numbers4_prediction_candidates USING btree (number);


--
-- Name: numbers4_predictions_log_target_draw_number_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX numbers4_predictions_log_target_draw_number_idx ON public.numbers4_predictions_log USING btree (target_draw_number);


--
-- Name: predictions_createdAt_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "predictions_createdAt_idx" ON public.predictions USING btree ("createdAt");


--
-- Name: predictions_isPublic_isHidden_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "predictions_isPublic_isHidden_idx" ON public.predictions USING btree ("isPublic", "isHidden");


--
-- Name: predictions_lotteryType_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "predictions_lotteryType_idx" ON public.predictions USING btree ("lotteryType");


--
-- Name: predictions_targetDrawNumber_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "predictions_targetDrawNumber_idx" ON public.predictions USING btree ("targetDrawNumber");


--
-- Name: predictions_userId_idx; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX "predictions_userId_idx" ON public.predictions USING btree ("userId");


--
-- Name: users_email_key; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);


--
-- Name: users_username_key; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);


--
-- Name: comments comments_predictionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT "comments_predictionId_fkey" FOREIGN KEY ("predictionId") REFERENCES public.predictions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: comments comments_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT "comments_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: likes likes_predictionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT "likes_predictionId_fkey" FOREIGN KEY ("predictionId") REFERENCES public.predictions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: likes likes_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT "likes_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: predictions predictions_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT "predictions_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 9wCs4PcioSDiUGYBc15k8OJZDKnXQQZ0sfmd4bFWxKAZK8I8r7FYMl9kZBu89U6


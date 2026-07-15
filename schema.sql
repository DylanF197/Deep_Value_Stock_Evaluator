--
-- PostgreSQL database dump
--

\restrict KYKEJmtwB88CdZ4XDUxX8P4QawfSr8vjTXE373u9PiJgGu4lSqr1OCkYdZkBHzT

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: stocks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stocks (
    id integer NOT NULL,
    ticker character varying(10) NOT NULL,
    market_cap numeric,
    total_debt numeric,
    cash numeric,
    preferred_stock numeric,
    minority_interest numeric,
    enterprise_value numeric,
    ebit numeric,
    acquirers_multiple numeric,
    fetched_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    close_price numeric,
    sector character varying(50),
    industry character varying(50)
);


ALTER TABLE public.stocks OWNER TO postgres;

--
-- Name: stocks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stocks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stocks_id_seq OWNER TO postgres;

--
-- Name: stocks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stocks_id_seq OWNED BY public.stocks.id;


--
-- Name: stocks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stocks ALTER COLUMN id SET DEFAULT nextval('public.stocks_id_seq'::regclass);


--
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict KYKEJmtwB88CdZ4XDUxX8P4QawfSr8vjTXE373u9PiJgGu4lSqr1OCkYdZkBHzT


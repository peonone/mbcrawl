--
-- PostgreSQL database dump
--

-- Dumped from database version 10.4
-- Dumped by pg_dump version 10.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;



SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: products_beibei; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products_beibei (
    id integer NOT NULL,
    name character varying(512),
    description character varying(1024),
    category character varying(128)
);


--
-- Name: sku_images_beibei; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sku_images_beibei (
    product_id integer,
    sku_attr_code character varying(512),
    uploaded_path character varying(1024)
);


--
-- Name: skus_beibei; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.skus_beibei (
    id integer NOT NULL,
    name character varying(512),
    product_id integer,
    price integer,
    origin_price integer,
    stock integer,
    img_sku_attr_code character varying(512)
);


--
-- Name: products_beibei products_beibei_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products_beibei
    ADD CONSTRAINT products_beibei_pk PRIMARY KEY (id);


--
-- Name: skus_beibei skus_beibei_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skus_beibei
    ADD CONSTRAINT skus_beibei_pk PRIMARY KEY (id);


--
-- Name: ix_sku_images_beibei_prod; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sku_images_beibei_prod ON public.sku_images_beibei USING btree (product_id);


--
-- Name: ix_sku_images_beibei_sku_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sku_images_beibei_sku_code ON public.sku_images_beibei USING btree (sku_attr_code);


--
-- Name: ix_skus_beibei_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_skus_beibei_product_id ON public.skus_beibei USING btree (product_id);


--
-- PostgreSQL database dump complete
--


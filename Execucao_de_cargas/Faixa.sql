select distinct on (frt.title)
    p."name" AS "CLIENTE",
    vu."name" AS "OPERADOR",
    frt.title AS "title",
    fn.title AS "NATUREZA FINANCE",
    frt.entry_date AS "DATA_EMISSAO",
    pf.title AS "PAGAMENTO",  
    case
    	when p.cell_phone_1 is null then p.phone
    	else p.cell_phone_1
    end as "CONTATO",
    case
    	when t.total_amount is null then frt.v_final_amount
    	else t.total_amount
    end as "VALOR_TOTAL",
    frt.renegotiated as "RENEGOCIADO",
    t.receipt_date AS Date_last_paid,
    t.total_amount as "Val_last_paid",
    o.financial_title_occurrence_type_id as "Tipo_doc",
	CASE 
		WHEN POSITION('a partir da renegociação dos títulos ' IN o.description::text) > 0 THEN SUBSTRING(o.description::text, 
			POSITION('a partir da renegociação dos títulos' IN o.description::text) + LENGTH('a partir da renegociação dos títulos') + 1,
			POSITION('/' IN o.description::text) - (POSITION('a partir da renegociação dos títulos' IN o.description::text) + LENGTH('a partir da renegociação dos títulos') + 1)
			)
		ELSE NULL
	END as titulo_vinculado,  
    CASE
        WHEN EXISTS (SELECT * FROM erp.financial_receipt_titles t WHERE t.financial_receivable_title_id = frt.id) THEN '0'
        ELSE CURRENT_DATE - frt.expiration_date
    END AS Days_open,  
    CASE
        WHEN t.receipt_date IS NULL THEN 'ABERTO'
        ELSE 'PAGO'
    END AS "STATUS_PAGAMENTO",
    case
    	when frt.complement ilike '%renegociação%' then 'RENEGOCIADO'
	    else 'NÃO RENEGOCIADO'
    end as "RENEGOCIADO",
    CASE
        WHEN frt.expiration_date = frt.original_expiration_date THEN 'NÃO REAGENDADO'
        ELSE 'REAGENDADO'
    END AS "REAGENDAMENTO",
    frt.expiration_date AS "VCTO",
    case
	    when EXISTS (SELECT * FROM erp.financial_receipt_titles t WHERE t.financial_receivable_title_id = frt.id) THEN 'PAGO'
    	WHEN CURRENT_DATE - frt.expiration_date > 0 then 'VENCIDO'
        ELSE 'A VENCER'
    end "STATUS_RECEBIMENTO"
FROM
    financial_receivable_titles frt
INNER JOIN
    erp.financers_natures fn ON fn.id = frt.financer_nature_id
LEFT JOIN
    erp.financial_receipt_titles t ON t.financial_receivable_title_id = frt.id
left join 
	financial_receivable_title_occurrences o on o.financial_receivable_title_id = frt.id 
LEFT JOIN
    erp.v_users vu ON vu.id = frt.created_by
LEFT JOIN
    payment_forms pf ON t.payment_form_id = pf.id  
left join
	contracts c on c.id = frt.contract_id
INNER JOIN
    erp.people p ON p.id = frt.client_id
WHERE frt.deleted != true
	and frt.entry_date between '2025-01-01' and '2026-12-31'
    and o.financial_title_occurrence_type_id in (1,6)
    and frt.title ilike 'fat%'
package com.example.camel_mysql;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.component.sql.SqlComponent;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.util.Map;
import java.util.List;

@Component
public class JdAnalysisDataTransferRoute extends RouteBuilder {

    private final DataSource dataSource;

    public JdAnalysisDataTransferRoute(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void configure() throws Exception {

        // Set up SQL Component for Camel
        SqlComponent sqlComponent = new SqlComponent();
        sqlComponent.setDataSource(dataSource);
        getContext().addComponent("sql", sqlComponent);

        // Periodically fetch and process data
        from("timer://updateJdAnalysis?period=300000")
        .log("Starting JD Analysis data transfer...")

        // Modify the SQL query to conditionally check the papertype
        .to("sql:SELECT r.companyid, r.jobid, r.papertype, c.source AS sourcecode, " +
                "COUNT(*) AS registration_count, " +
                "SUM(CASE WHEN r.status != 'I' THEN 1 ELSE 0 END) AS registration_status_not_i_count, " +
                // If papertype is 'I', count status = 'O'; otherwise count status = 'P'
                "SUM(CASE WHEN r.papertype = 'I' AND r.status = 'O' THEN 1 " +
                "           WHEN r.papertype != 'I' AND r.status = 'P' THEN 1 ELSE 0 END) AS efficiency_count " + 
                "FROM registration r " +
                "JOIN candidate c ON r.candidateid = c.id " +
                "GROUP BY r.companyid, r.jobid, r.papertype, c.source")
        .split(body())
        .process(exchange -> {
            // Log the row data to check the headers before passing them to the SQL query
            Map<String, Object> row = exchange.getIn().getBody(Map.class);
            exchange.getIn().setHeaders(row);
            exchange.getIn().setHeader("companyid", row.get("companyid"));
            exchange.getIn().setHeader("sourcecode", row.get("sourcecode"));
            exchange.getIn().setHeader("papertype", row.get("papertype"));
            exchange.getIn().setHeader("jobid", row.get("jobid"));
            exchange.getIn().setHeader("registration_count", row.get("registration_count"));
            exchange.getIn().setHeader("submission", row.get("registration_status_not_i_count"));
            exchange.getIn().setHeader("efficiency", row.get("efficiency_count"));  // Save efficiency count
        })

        // Check if record exists in jdanalysis table
        .to("sql:SELECT COUNT(*) AS exists_count FROM jdanalysis WHERE companyid = :#companyid " +
                "AND sourcecode = :#sourcecode AND papertype = :#papertype AND jobid = :#jobid")
        .process(exchange -> {
            List<Map<String, Object>> result = exchange.getIn().getBody(List.class);
            Integer existsCount = ((Number) result.get(0).get("exists_count")).intValue();
            exchange.getIn().setHeader("exists_count", existsCount);
        })

        .choice()
        .when(simple("${header.exists_count} > 0"))
            .log("Updating record for companyid: ${header.companyid}, sourcecode: ${header.sourcecode}, papertype: ${header.papertype}, jobid: ${header.jobid}")
            .to("sql:UPDATE jdanalysis SET registration = :#registration_count, " +
                    "submission = :#submission, " +
                    "efficiency = :#efficiency " +  // Update efficiency field
                    "WHERE companyid = :#companyid AND sourcecode = :#sourcecode " +
                    "AND papertype = :#papertype AND jobid = :#jobid")
        .otherwise()
            .log("Inserting new record for companyid: ${header.companyid}, sourcecode: ${header.sourcecode}, papertype: ${header.papertype}, jobid: ${header.jobid}")
            .to("sql:INSERT INTO jdanalysis (companyid, sourcecode, papertype, jobid, registration, submission, efficiency) " +
                    "VALUES (:#companyid, :#sourcecode, :#papertype, :#jobid, :#registration_count, :#submission, :#efficiency)")  // Insert efficiency
        .end()

        .log("JD Analysis data transfer completed.");


    }
}
